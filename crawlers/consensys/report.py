import re
INVALID_FS_CHARS = r'[<>:"/\\|?*]'

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from configs.consensys.project import PROJECT_LIST_PATH
from configs.consensys.report import (
    REPORT_DATA_PATH,
    REPORT_ERROR_LOG_PATH,
)
from ..base.report import ReportCrawlerBase, ReportCrawlerConfig
from helpers.selenium import (
    extract_links,
    extract_codes,
    extract_nested_list,
    extract_class,
    extract_tags,
    extract_tag_names_in,
)


class ReportCrawler(ReportCrawlerBase):
    def __init__(self, options: list[str], root_dir: str = ""):
        config = ReportCrawlerConfig(
            root_dir=root_dir,
            project_list_path=PROJECT_LIST_PATH,
            report_data_path=REPORT_DATA_PATH,
            error_file_path=REPORT_ERROR_LOG_PATH,
            title_tag="h2",
            subtitle_tag="h3",
            smtitle_tag="h4",
        )
        super().__init__(options, config)

    def __split(
        self, section: WebElement | list[WebElement], title_tag: str
    ) -> list[list[WebElement]]:
        """
        functionality:
            split section by title_tag passed, each section starts with a titla_tag
        return value:
            list of section, each section is a list of WebElement
        """
        elements = section
        section_list, section_tmp = [], []

        # if elements is a single element, get elements in the section
        if isinstance(elements, WebElement):
            elements = section.find_elements(By.XPATH, "./*")

        for element in elements:
            if element.tag_name == title_tag:
                section_list.append(section_tmp)
                section_tmp = []

            # issue is only in subsection
            if title_tag == self.subtitle_tag and "issue" in extract_class(element):
                section_list.append(section_tmp)
                section_tmp = []

            section_tmp.append(element)
        section_list.append(section_tmp)

        if not section_list[0] or section_list[0][0].tag_name == "aside":
            section_list = section_list[1:]
        return section_list

    # handle element in details in place
    def __extract_basic_info(
        self, element: WebElement, title: str, title_tag: str, detail: dict
    ) -> None:
        """
        extract basic info in the section
        """
        detail["links"].extend(extract_links(element))
        detail["codes"].extend(extract_codes(element))

        if element.tag_name == title_tag:
            detail[title] = element.text
        elif element.tag_name == "p":
            detail["content"].append(element.text)
        elif element.tag_name in ["ul", "ol"]:
            detail["content"].append(extract_nested_list(element))
        elif element.tag_name == "table":
            rows = element.find_elements(By.TAG_NAME, "tr")
            rows = [extract_tags(row, "td") for row in rows]

            # filther out empty rows and ["", "", ""] rows
            table = {
                "column": extract_tags(element, "th"),
                "rows": [row for row in rows if row and any(row)],
            }
            detail["content"].append(table)
        elif element.tag_name == "div":
            classes = extract_class(element)
            # Skip interactive menu containers (export to GitHub/clipboard/etc.)
            # which are added to issues in newer report pages.
            if "menu-container" in classes or "menu-box" in classes:
                return
            if "highlight" in classes:
                detail["codes"].append(element.text)
            # Avoid appending empty strings from decorative divs
            if element.text.strip():
                detail["content"].append(element.text)

    def handle_issue(self, smsection: list[WebElement]) -> list[dict]:
        details = []
        elements = smsection.find_elements(By.XPATH, "./*")
        for element in elements:
            if element.tag_name != "div":
                continue
            if "resolution" in extract_class(element):
                detail = {
                    "smtitle": "smtitle_not_found",
                    "content": [],
                    "links": [],
                    "codes": [],
                }
                sm_element = element.find_elements(By.XPATH, "./*")
                for sm in sm_element:
                    child_tags = extract_tag_names_in(sm)
                    # find if any element p tag or ul tag under the sm
                    if "p" in child_tags or "ul" in child_tags:
                        for child in sm.find_elements(By.XPATH, "./*"):
                            self.__extract_basic_info(
                                child, "smtitle", self.smtitle_tag, detail
                            )
                    else:
                        self.__extract_basic_info(
                            sm, "smtitle", self.smtitle_tag, detail
                        )
                details.append(detail)
            else:
                smsection_list = self.__split(element, self.smtitle_tag)
                for smsection in smsection_list:
                    details.append(self.handle_smsection(smsection))
        return details

    def handle_smsection(self, smsection: list[WebElement]):
        detail = {
            "smtitle": "smtitle_not_found",
            "content": [],
            "links": [],
            "codes": [],
        }
        for element in smsection:
            self.__extract_basic_info(element, "smtitle", self.smtitle_tag, detail)
        return detail

    def handle_subsection(self, subsection: list[WebElement]):
        detail = {
            "subtitle": "subtitle_not_found",
            "content": [],
            "links": [],
            "codes": [],
        }
        for element in subsection:
            subtitle = self.subtitle_tag
            if "issue" in extract_class(element):
                # if issue is in subsection, then issue is the only one element in the subsection
                detail["subtitle"] = element.find_element(By.TAG_NAME, subtitle).text
                detail["content"] = self.handle_issue(element)
                continue
            self.__extract_basic_info(element, "subtitle", subtitle, detail)
        return detail

    def handle_section(self, section: list[WebElement]) -> dict:
        detail = {"title": "title_not_found", "content": [], "links": [], "codes": []}
        section_without_title = []
        for element in section:
            if element.tag_name == self.title_tag:
                detail["title"] = element.text
            else:
                section_without_title.append(element)
        subsection_list = self.__split(section_without_title, self.subtitle_tag)
        for subsection in subsection_list:
            detail["content"].append(self.handle_subsection(subsection))
        return detail

    def crawl(self, project_url: str, project_name: str):
        self.set_current_project(project_name)
        self.load_page(project_url)
        report = self.driver.find_element(By.CLASS_NAME, "dili-navigator-content")
        section_list = self.__split(report, self.title_tag)
        details = {"details": []}
        for section in section_list:
            details["details"].append(self.handle_section(section))
        self.save_report_data(details)

    def crawl_all(self):
        project_list = self.load_project_list()
        for project in project_list:
            try:
                project_name = project["project_name"]
                project_url = project["report_link"]
                print(f"Crawling {project_name}...")
                if "github" not in project_url and not project_url.endswith(".pdf"):
                    self.crawl(project_url, project_name)
            except Exception as e:
                self.log_error(project_name, e)

        self.driver.quit()
