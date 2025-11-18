import os
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from tqdm import tqdm

from helpers.report import (
    get_all_links_from_report,
    get_languages_from_project_url,
    analyze_links_info,
    create_tqdm_title,
)


@dataclass
class AnalyzerConfig:
    root_dir: str
    project_list_path: str
    report_data_path: str
    analysis_data_path: str
    analysis_error_path: str


class AnalyzerBase(ABC):
    def __init__(self, config: AnalyzerConfig):
        self.project_list_path = config.project_list_path.format(
            root_dir=config.root_dir
        )
        self.report_data_path = config.report_data_path.format(
            root_dir=config.root_dir, name="{name}"
        )
        self.report_data_dir_path = "/".join(self.report_data_path.split("/")[0:-1])
        self.analysis_data_path = config.analysis_data_path.format(
            root_dir=config.root_dir, name="{name}"
        )
        self.analysis_error_path = config.analysis_error_path.format(
            root_dir=config.root_dir, name="{name}"
        )
        self.analysis_error_dir_path = "/".join(
            self.analysis_error_path.split("/")[0:-1]
        )

        os.makedirs(self.analysis_error_dir_path, exist_ok=True)
        if not os.path.exists(self.project_list_path):
            raise FileNotFoundError(f"{self.project_list_path} not found.")

    def get_project_name_from_path(self, path: str):
        return path.split("/")[-1].split(".json")[0]

    def save_analysis_data(self, data: dict):
        with open(self.analysis_data_path, "w") as f:
            json.dump(data, f)

    def save_analysis_error(self, error_msg: str):
        with open(self.analysis_error_path, "a") as f:
            f.write(error_msg + "\n")

    def load_json_file(self, file_path: str):
        with open(file_path, "r") as f:
            return json.load(f)

    def get_reports_file_paths(self) -> list[str]:
        files = []
        for root, _, filenames in os.walk(self.report_data_dir_path):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files

    def load_project_list(self):
        try:
            projects = self.load_json_file(self.project_list_path)
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON file: {self.project_list_path}")
        if not isinstance(projects, list):
            raise Exception(f"Project list data not a list: {self.project_list_path}")
        return projects

    def get_overall_projects_info(self):
        projects = self.load_project_list()
        analysis = {
            "total": len(projects),
            "github": 0,
            "pdf": 0,
        }
        # using tqdm to show progress bar
        title = create_tqdm_title("Overall projects info")
        for project in tqdm(projects, desc=title):
            report_link = project["report_link"]
            if "https://github.com" in report_link:
                analysis["github"] += 1
            elif report_link.endswith(".pdf"):
                analysis["pdf"] += 1
        return analysis

    def get_links_info_of_reports(self) -> dict[str, dict[str, int]]:
        """
        Each report contains a list of links.
        This function will analyze the links in each report.
        """
        # get all file under self.report_data_dir_path
        reports_links_info = {}
        report_file_paths = self.get_reports_file_paths()
        title = create_tqdm_title("Links info of reports")
        for file_path in tqdm(report_file_paths, desc=title):
            report_name = file_path.split("/")[-1].split(".")[0]
            try:
                report = self.load_json_file(file_path)
                links = get_all_links_from_report(report)
                info = analyze_links_info(links, check_broken=False)
                reports_links_info[report_name] = info
            except Exception as e:
                self.save_analysis_error(f"Error in {file_path}: {e}")
        return reports_links_info

    def get_languages_of_projects(self) -> dict[str, int]:
        languages = {}
        projects = self.load_project_list()
        title = create_tqdm_title("Languages of projects")
        for project in tqdm(projects, desc=title):
            projects_name = project["project_name"]
            report_link = project["report_link"]
            project_languages = get_languages_from_project_url(report_link)
            languages[projects_name] = project_languages
        return languages

    @abstractmethod
    def analyze(self):
        pass
