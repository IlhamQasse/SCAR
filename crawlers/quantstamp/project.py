import json
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
from configs.quantstamp.project import (
    QUANTSTAMP_URL,
    TABLE_CONTAINER_XPATH,
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
        self.url = QUANTSTAMP_URL
        self.max_retries = MAX_RETRIES

        # Initialize WebDriver
        self.driver = webdriver.Chrome(options=self.options)

    def load_page(self, url):
        # Navigate to the website
        self.driver.get(url)

        # wait until the page is loaded
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

    def scroll_to_bottom(self, div: WebElement):
        cnt, retry = 0, 0
        script = "arguments[0].scrollTop = arguments[0].scrollHeight"
        while True:
            self.driver.execute_script(script, div)
            sleep(1)
            total = len(div.find_elements(By.TAG_NAME, "tr"))
            if total != cnt:
                cnt, retry = total, 0
            elif retry >= self.max_retries:
                break
            else:
                retry += 1

    def write_to_file(self, trs: List[WebElement]):
        rows = []
        for tr in trs:
            row = []
            tds = tr.find_elements(By.TAG_NAME, "td")
            for td in tds:
                if td.find_elements(By.TAG_NAME, "a"):
                    a = td.find_element(By.TAG_NAME, "a")
                    row.append(a.get_attribute("href"))
                else:
                    text = " ".join(td.text.split("\n"))
                    row.append(text)
            row_in_json = {
                "project_name": row[0],
                "category": row[1],
                "ecosystem": row[2],
                "language": row[3],
                "date": row[4],
                "report_link": row[5],
            }

            # row in json with lower case keys
            rows.append(row_in_json)
        with open(self.data_path, "w") as f:
            json.dump(rows, f, indent=4)

    def crawl_all(self):
        if self.driver is None:
            return
        try:
            self.load_page(self.url)
            # find the div by xpath
            div = self.driver.find_element(By.XPATH, TABLE_CONTAINER_XPATH)
            self.scroll_to_bottom(div)
            table = div.find_element(By.TAG_NAME, "table")
            tbody = table.find_element(By.TAG_NAME, "tbody")
            trs = tbody.find_elements(By.TAG_NAME, "tr")
            self.write_to_file(trs)

        finally:
            self.driver.quit()
