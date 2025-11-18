import os
import json
import base64
from dataclasses import dataclass

from .github import GitHubCrawler
from helpers.report import get_all_links_from_report
from configs.base.types import ReportFile, ReportLink


@dataclass
class RepoCrawlerBaseConfig:
    token: str
    root_dir: str
    report_dir_path: str
    repo_data_dir_path: str


class RepoCrawlerBase:
    def __init__(self, config: RepoCrawlerBaseConfig):
        self.token = config.token
        self.root_dir = config.root_dir
        self.report_dir_path = config.report_dir_path
        self.repo_data_dir_path = config.repo_data_dir_path
        self.github_crawler = GitHubCrawler(self.token)
        self.report_files: list[ReportFile] | None = None

        if not os.path.exists(self.repo_data_dir_path):
            os.makedirs(self.repo_data_dir_path, exist_ok=True)

    def load_report_files(self):
        # walk dir and load reports
        report_files = []
        for root, _, files in os.walk(self.report_dir_path):
            report_files = [
                {
                    "file_path": os.path.join(root, file),
                    "report_name": file.rstrip(".json"),
                }
                for file in files
            ]
        return report_files

    def extract_links(self, json_data: dict | list) -> list[str]:
        return get_all_links_from_report(json_data)

    def get_github_repo_data(self, url: str) -> dict | str | None:
        try:
            return self.github_crawler.fetch_data(url)
        except Exception as e:
            return None

    def load_report_content(self, report_file: ReportFile):
        with open(report_file["file_path"], "r") as file:
            return json.load(file)

    def save_github_repo_data(
        self, report_name: str, report_link: ReportLink, data: dict | str
    ):
        data["report_name"] = report_name
        data["report_link_url"] = report_link["url"]
        data["report_link_hypertext"] = report_link["hypertext"]
        data_file_name = base64.b64encode(report_link["url"].encode()).decode()
        storage_dir_path = os.path.join(
            self.repo_data_dir_path, report_name.replace(" ", "_")
        )
        if not os.path.exists(storage_dir_path):
            os.makedirs(storage_dir_path, exist_ok=True)
        storage_fil_path = os.path.join(storage_dir_path, f"{data_file_name}.json")
        with open(storage_fil_path, "w") as file:
            json.dump(data, file, indent=4)

    def crawl(self, report_file: ReportFile):
        content = self.load_report_content(report_file)
        report_name = report_file["report_name"]
        links = self.extract_links(content)
        for link in links:
            data = self.get_github_repo_data(link["url"])
            if data is not None:
                self.save_github_repo_data(report_name, link, data)

    def crawl_all(self):
        self.report_files = self.load_report_files()
        for report_file in self.report_files:
            self.crawl(report_file)
