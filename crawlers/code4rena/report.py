from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from configs.code4rena.project import PROJECT_LIST_PATH
from configs.code4rena.report import (
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

            # In older reports Code4rena wrapped findings in a div with class
            # "issue"; newer reports simply use a heading (e.g. h2) for each
            # finding.  Splitting on the subtitle tag already handles new
            # findings, so we no longer rely on the presence of an "issue"
            # class to start a new subsection.

            section_tmp.append(element)
        section_list.append(section_tmp)

        if not section_list[0] or section_list[0][0].tag_name == "aside":
            section_list = section_list[1:]
        return section_list

    def set_project_title_tag(self):
        self.title_tag = "h1"
        self.subtitle_tag = "h2"
        self.smtitle_tag = "h3"

    # handle element in details in place
    def __extract_basic_info(
        self, element: WebElement, title: str, title_tag: str, detail: dict
    ) -> None:
        """
        extract basic info in the section
        """
        detail["links"].extend(extract_links(element))
        detail["codes"].extend(extract_codes(element))
        detail["blockquotes"].extend(extract_tags(element, "blockquote"))
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

    def handle_smsection(self, smsection: list[WebElement]) -> list[dict]:
        detail = {
            "smtitle": "not_found",
            "content": [],
            "links": [],
            "codes": [],
            "blockquotes": [],
        }
        for element in smsection:
            self.__extract_basic_info(element, "smtitle", self.smtitle_tag, detail)
        return detail

    def handle_subsection(self, subsection: list[WebElement]):
        detail = {
            "subtitle": "not_found",
            "content": [],
            "links": [],
            "codes": [],
            "blockquotes": [],
        }
        has_smsection = any(el.tag_name == self.smtitle_tag for el in subsection)
        if not has_smsection:
            for element in subsection:
                self.__extract_basic_info(
                    element, "subtitle", self.subtitle_tag, detail
                )
        else:
            subsection_without_subtitle = []
            for element in subsection:
                if element.tag_name == self.subtitle_tag:
                    detail["subtitle"] = element.text
                else:
                    subsection_without_subtitle.append(element)
            smsection_list = self.__split(subsection_without_subtitle, self.smtitle_tag)
            for smsection in smsection_list:
                detail["content"].append(self.handle_smsection(smsection))
        return detail

    def handle_section(self, section: list[WebElement]) -> dict:
        detail = {"title": "not_found", "content": []}
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
        report = self.driver.find_element(By.CLASS_NAME, "report-contents")
        section_list = self.__split(report, self.title_tag)
        details = {"details": []}
        for section in section_list:
            details["details"].append(self.handle_section(section))
        self.save_report_data(details)

    def crawl_all(self):
        self.set_project_title_tag()
        project_list = self.load_project_list()
        for project in project_list:
            try:
                project_name = project["project_name"]
                project_url = project["report_link"]
                print(f"crawling {project_name}...")
                if "github" not in project_url:
                    self.crawl(project_url, project_name)
            except Exception as e:
                self.log_error(project_name, e)
        self.driver.quit()
