import json
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from configs.openzeppelin.project import PROJECT_LIST_PATH
from configs.openzeppelin.report import (
    REPORT_DATA_PATH,
    REPORT_ERROR_LOG_PATH,
)
from ..base.report import ReportCrawlerBase, ReportCrawlerConfig
from helpers.selenium import (
    extract_links,
    extract_codes,
    extract_dl,
    extract_nested_list,
)


class ReportCrawler(ReportCrawlerBase):
    def __init__(self, options: list[str], root_dir: str = ""):
        # Initialize WebDriver
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

            section_tmp.append(element)
        section_list.append(section_tmp)

        if not section_list[0]:
            section_list = section_list[1:]
        return section_list

    def handle_subsection(self, subsection: list[WebElement]) -> dict:
        detail = {
            "subtitle": "subtitle_not_found",
            "content": [],
            "blockquote": [],
            "links": [],
            "codes": [],
        }
        for element in subsection:
            if element.tag_name == self.subtitle_tag:
                detail["subtitle"] = element.text
            elif element.tag_name == "p":
                detail["content"].append(element.text)
            elif element.tag_name == self.smtitle_tag:
                detail["content"].append(f"'{element.text}'")
            elif element.tag_name in ["ul", "ol"]:
                detail["content"].append(extract_nested_list(element))
                # detail["content"].append(extract_tags(element, "li"))
            elif element.tag_name == "dl":
                detail["content"].append(extract_dl(element))
            elif element.tag_name == "blockquote":
                detail["blockquote"].append(element.text)
            else:
                content = element.text.split("\n")
                content = [x for x in content if x not in ["", " "]]
                if content:
                    detail["content"].append(content)
            detail["links"].extend(extract_links(element))
            detail["codes"].extend(extract_codes(element))
        return detail

    def handle_section(self, section: list[WebElement]) -> dict:
        """
        functionality:
            handle each section, section's title starts with an h2 or h3 tag
        return value:
            dict of section detail
        """
        detail = {"title": "title_not_found", "content": []}

        # get title, if not found, set title to "title_not_found"
        section_without_title = []
        for element in section:
            if element.tag_name == self.title_tag:
                detail["title"] = element.text
            else:
                section_without_title.append(element)

        # handle subsection
        subsection_list = self.__split(section_without_title, self.subtitle_tag)
        for subsection in subsection_list:
            res = self.handle_subsection(subsection)
            detail["content"].append(res)
        return detail

    def crawl(self, url: str, project_name: str):
        self.load_page(url)
        report_container = self.driver.find_element(By.ID, "hs_cos_wrapper_post_body")
        # set current project dir and name
        self.set_current_project(project_name)

        # set title tag
        self.set_project_title_tag(report_container)
        section_list = self.__split(report_container, self.title_tag)
        details = {"details": []}
        for section in section_list:
            res = self.handle_section(section)
            details["details"].append(res)
        with open(f"{self.current_project_dir}.json", "w") as f:
            json.dump(details, f, indent=4)

    def crawl_all(self):
        project_list = self.load_project_list()
        for project in project_list:
            try:
                project_name = project["project_name"]
                project_url = project["report_link"]
                print(f"Crawling {project_name}...")
                self.crawl(project_url, project_name)
            except Exception as e:
                self.log_error(project_name, e)
        self.driver.quit()
