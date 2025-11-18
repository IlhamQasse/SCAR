import os
import json
from abc import ABC, abstractmethod
from selenium import webdriver
from dataclasses import dataclass
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
import re            # ← ADD THIS
from pathlib import Path


from helpers.selenium import get_title_tag


INVALID_FS_CHARS = r'[<>:"/\\|?*]'

def _safe_filename(stem: str, ext: str) -> str:
    # replace invalid characters with ' - '
    stem = re.sub(INVALID_FS_CHARS, " - ", stem)
    # collapse whitespace and trim trailing space/dot (Windows limitation)
    stem = re.sub(r"\s+", " ", stem).strip(" .")
    # keep it reasonably short
    if len(stem) > 200:
        stem = stem[:200].rstrip()
    return f"{stem}{ext}"

@dataclass
class ReportCrawlerConfig:
    root_dir: str
    project_list_path: str
    report_data_path: str
    error_file_path: str
    title_tag: str
    subtitle_tag: str
    smtitle_tag: str


class ReportCrawlerBase(ABC):
    def __init__(self, options: list[str], config: ReportCrawlerConfig):
        # Initialize WebDriver
        self.options = Options()
        for option in options:
            self.options.add_argument(option)

        try:
            self.driver = webdriver.Chrome(options=self.options)
        except Exception as e:
            print(e)
            exit(1)

        # Report directory path of project
        self.project_list_path = config.project_list_path.format(
            root_dir=config.root_dir
        )
        self.report_data_path = config.report_data_path.format(
            root_dir=config.root_dir, name="{name}"
        )
        self.error_file_path = config.error_file_path.format(
            root_dir=config.root_dir, name="{name}"
        )
        self.error_dir_path = self.error_file_path.split("{name}")[0]

        # Current project for the crawler
        self.current_project_report_path = ""
        self.current_project_name = ""
        self.title_tag = config.title_tag
        self.subtitle_tag = config.subtitle_tag
        self.smtitle_tag = config.smtitle_tag

        # Check if the file exists, if not, raise an error
        if not os.path.exists(self.project_list_path):
            raise FileNotFoundError(f"{self.project_list_path} not found.")

        # check if data store dir, if not, create the directory
        if not os.path.exists(self.report_data_path.split("{name}")[0]):
            os.makedirs(os.path.dirname(self.report_data_path), exist_ok=True)

        if not os.path.exists(self.error_dir_path):
            os.makedirs(self.error_dir_path, exist_ok=True)

    def load_project_list(self):
        with open(self.project_list_path, "r") as f:
            return json.load(f)

    def save_report_data(self, data: dict):
        dir_path, base = os.path.split(self.current_project_report_path)
        root, ext = os.path.splitext(base)
        safe_base = _safe_filename(root, ext or ".json")
        safe_report_path = os.path.join(dir_path, safe_base)

        os.makedirs(dir_path, exist_ok=True)
        with open(safe_report_path, "w") as f:
            json.dump(data, f, indent=4)
        self.current_project_report_path = safe_report_path


    def log_error(self, project_name: str, exc: Exception):
        """
        Log an exception encountered while processing a project.

        When an exception is raised during crawling, this helper writes
        a concise message to a per-project error file inside the
        configured error directory. The filename is sanitized via
        ``_safe_filename`` to avoid invalid filesystem characters.

        Parameters
        ----------
        project_name: str
            Name of the project being processed when the error occurred.
        exc: Exception
            The exception instance that was raised.
        """
        try:
            # Ensure the error directory exists.  Use the configured
            # directory path derived from ``error_file_path`` rather than
            # the undefined ``errors_dir`` attribute.
            os.makedirs(self.error_dir_path, exist_ok=True)

            # Create a safe filename for the error log based on the project name
            error_file = _safe_filename(project_name, ".txt")
            error_file_path = os.path.join(self.error_dir_path, error_file)

            # Append the exception details to the error log file
            with open(error_file_path, "a", encoding="utf-8") as f:
                f.write(f"{type(exc).__name__}: {exc}\n")
        except Exception as e2:
            # Last resort: if writing the error log fails, report it to stdout
            print(f"[WARN] Failed to write error log for {project_name!r}: {e2}")


    def set_current_project(self, project_name: str) -> None:
        project_name = project_name.replace("/", "\\")
        self.current_project_report_path = (
            self.report_data_path.format(name=project_name) + ".json"
        )
        self.current_project_name = project_name

    def set_project_title_tag(self, report_container: WebElement):
        self.title_tag = get_title_tag(report_container)
        self.subtitle_tag = "h3" if self.title_tag == "h2" else "h4"
        self.smtitle_tag = "h4" if self.title_tag == "h2" else "h5"

    def load_page(self, url, main_tag="main", timeout=10):
        # Navigate to the website
        self.driver.get(url)

        # wait until the page is loaded
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, main_tag))
        )

    @abstractmethod
    def crawl_all(self):
        pass
