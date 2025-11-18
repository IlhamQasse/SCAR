import dotenv
import os
import threading
from crawl import crawler_factory
from analyze import analyzer_factory
from crawlers.base.report import ReportCrawlerBase
from configs.base.types import Platform


def run_crawler(crawler: ReportCrawlerBase):
    crawler.crawl_all()


def run_crawler_in_threads(crawlers: list[ReportCrawlerBase]):
    threads = []
    for crawler in crawlers:
        thread = threading.Thread(target=run_crawler, args=(crawler,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":

    # init configs
    dotenv.load_dotenv(dotenv_path=".env.local")
    token = os.getenv(key="GITHUB_ACCESS_TOKEN")
    root_dir = os.path.dirname(__file__)

    for platfrom in Platform:
        platfrom_dir = platfrom.value.lower()
        os.makedirs(os.path.join(root_dir, "data", platfrom_dir), exist_ok=True)

    options = ["--headless", "--no-sandbox", "--disable-dev-shm-usage"]
    crawler_types = ["project", "report", "repo"]

    # create crawlers and run in parallel
    for crawler_type in crawler_types:
        crawlers = crawler_factory(crawler_type, "all", options, root_dir, token)
        run_crawler_in_threads(crawlers)

    # create crawlers and run
    analyzers = analyzer_factory("all", root_dir)
    for analyzer in analyzers:
        analyzer.analyze()
