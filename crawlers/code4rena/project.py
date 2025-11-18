import json
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from configs.code4rena.project import (
    CODE4RENA_URL,
    PROJECT_LIST_PATH,
    MAX_RETRIES,
)


class ProjectCrawler:
    def __init__(self, options: List[str] = [], root_dir: str = ""):
        # Initialize headless Chrome options
        self.options = Options()
        for option in options:
            self.options.add_argument(option)

        # Initialize configs
        self.data_path = PROJECT_LIST_PATH.format(root_dir=root_dir)
        self.url = CODE4RENA_URL
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

    def write_project_to_file(self, project_list: dict):
        with open(self.data_path, "w") as f:
            f.write(json.dumps(project_list, indent=4))

    def crawl(self):
        if self.driver is None:
            return
        projects = []
        self.load_page(self.url)
        project_list = self.driver.find_elements(By.CLASS_NAME, "report-tile")
        for project in project_list:
            try:
                tile_content = project.find_element(
                    By.CLASS_NAME, "report-tile__content"
                )
                tile_footer = project.find_element(By.CLASS_NAME, "report-tile__footer")
                project_name = tile_content.find_element(By.TAG_NAME, "h2").text
                project_name = project_name[0:-2]
                report_link = tile_content.find_element(By.TAG_NAME, "a").get_attribute(
                    "href"
                )
                period = tile_content.find_element(By.TAG_NAME, "p").text
                date = tile_footer.find_element(By.TAG_NAME, "p").text
                project = {
                    "project_name": project_name,
                    "report_link": report_link,
                    "period": period,
                    "date": date,
                }
                projects.append(project)
            except NoSuchElementException as e:
                print(e)
        self.write_project_to_file(projects)
        self.driver.quit()

    def crawl_all(self):
        try:
            self.crawl()
        except Exception as e:
            print(e)
