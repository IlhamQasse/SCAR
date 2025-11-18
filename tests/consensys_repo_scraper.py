import os
import dotenv
import sys

# Add the project root to the Python path to resolve imports
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)


if __name__ == "__main__":
    from crawlers.consensys.repo import RepoCrawler

    env_file_path = os.path.join(root_dir, ".env.local")
    dotenv.load_dotenv(dotenv_path=env_file_path)
    token = os.getenv(key="GITHUB_ACCESS_TOKEN")
    crawler = RepoCrawler(token, root_dir)
    crawler.crawl_all()
