import os
import argparse
import threading
import dotenv
from enum import Enum
from configs.base.types import Platform, CrawlerType
from crawlers.base.report import ReportCrawlerBase


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--type",
        type=str,
        required=True,
        help="report or project crawler",
    )
    parser.add_argument(
        "-p",
        "--platform",
        type=str,
        required=True,
        help="Platform to crawler projects from",
    )

    return parser.parse_args()


def crawler_instance(
    type: str, platform: str, options: list, root_dir: str, token: str | None = None
):
    print(f"Creating {type.capitalize()}Crawler for {platform}")
    module_path = f"crawlers.{platform.lower()}.{type}"
    class_name = f"{type.capitalize()}Crawler"
    module = __import__(module_path, fromlist=[class_name])
    crawler_class = getattr(module, class_name)

    # if type is repo, pass token as first argument
    if type == "repo":
        return crawler_class(token, root_dir)

    # if type is report, pass options as first argument
    return crawler_class(options, root_dir)


def crawler_factory(
    type: str, platform: str, options: list, root_dir: str, token: str | None = None
) -> list[ReportCrawlerBase]:
    ## initialize the list of types and platforms
    types = [m.value.lower() for m in CrawlerType]
    platfroms = [p.value.lower() for p in Platform]
    type, platform = type.lower(), platform.lower()
    crawlers = []

    # check if type is in the list of types
    if type not in types:
        raise ValueError(f"Type must be in {types}!")

    if platform == "all":
        for platform in platfroms:
            crawler = crawler_factory(type, platform, options, root_dir)
            crawlers.append(crawler[0])
    else:
        # Using platform + type to determine which crawler to run
        if platform not in platfroms:
            raise ValueError(f"Platform must be in {platfroms}")
        crawler = crawler_instance(type, platform, options, root_dir, token)
        crawlers.append(crawler)
    return crawlers


if __name__ == "__main__":

    # declare a function to run the crawler
    def run_crawler(crawler: ReportCrawlerBase):
        crawler.crawl_all()

    # initialize the root directory, and github access token
    root_dir = os.path.dirname(__file__)
    dotenv.load_dotenv(dotenv_path=".env.local")
    token = os.getenv(key="GITHUB_ACCESS_TOKEN")

    # parse the arguments
    args = parse_args()
    options = ["--headless", "--no-sandbox", "--disable-dev-shm-usage"]
    crawlers = crawler_factory(args.type, args.platform, options, root_dir, token)

    ## Run crawlers in parallel
    threads = []
    for crawler in crawlers:
        thread = threading.Thread(target=run_crawler, args=(crawler,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
