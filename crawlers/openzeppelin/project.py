import json
import time
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from configs.openzeppelin.project import (
    OPENZEPPELIN_URL,
    PROJECT_LIST_PATH,
    MAX_RETRIES,
    PAGE_NUM,
)


class ProjectCrawler:
    def __init__(self, options: List[str] = [], root_dir: str = ""):
        # Initialize headless Chrome options
        self.options = Options()
        for option in options:
            self.options.add_argument(option)

        # Initialize configs
        self.data_path = PROJECT_LIST_PATH.format(root_dir=root_dir)
        self.url = OPENZEPPELIN_URL
        self.max_retries = MAX_RETRIES

        # Initialize WebDriver
        self.driver = webdriver.Chrome(options=self.options)

    def load_page(self, url):
        # Navigate to the website
        self.driver.get(url)

        # wait until the page is loaded
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )

    def get_meta_data(self, link: str) -> str:
        self.load_page(link)
        res = self.driver.find_element(By.CLASS_NAME, "tags-wrapper")
        try:
            date = res.text.split("\n")[2].strip()
            return date
        except:
            return "N/A"

    def get_meta_data_for_projects(self, link: str):
        project_list: list[dict] = self.read_project_list__from_file()
        for i in range(len(project_list)):
            project = project_list[i]
            link = project["report_link"]
            project["date"] = self.get_meta_data(link)
            project.pop("author_name", None)
            project_list[i] = project
        self.write_project_to_file(project_list)

    def read_project_list__from_file(self):
        with open(self.data_path, "r") as f:
            projects = json.loads(f.read())
        return projects

    def write_project_to_file(self, project_list: dict):
        with open(self.data_path, "w") as f:
            f.write(json.dumps(project_list, indent=4))

    def crawl(self):
        if self.driver is None:
            return
        projects = []
        for i in range(1, PAGE_NUM + 1):
            try:
                self.load_page(self.url + f"/page/{i}")
                articles = self.driver.find_elements(By.TAG_NAME, "article")
                for article in articles:
                    link = article.find_element(
                        By.CLASS_NAME, "blog-listing__post-title-link"
                    )
                    description = article.find_element(By.TAG_NAME, "p")

                    related_tags = article.find_elements(
                        By.CLASS_NAME, "hs-blog-post-listing__post-tag"
                    )

                    project = {
                        "project_name": link.text,
                        "description": description.text or None,
                        "report_link": link.get_attribute("href"),
                        "related_tags": [tag.text for tag in related_tags],
                    }

                    projects.append(project)

                # find the div by xpath
            except NoSuchElementException as e:
                print(e)
            finally:
                time.sleep(1)
        self.write_project_to_file(projects)

    def crawl_all(self):
        try:
            self.crawl()
            self.get_meta_data_for_projects(self.url)
        except Exception as e:
            print(e)
        self.driver.quit()
