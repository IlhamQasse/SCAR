import os
import dotenv
import sys

# Add the project root to the Python path to resolve imports
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)


if __name__ == "__main__":
    from crawlers.base.github import GitHubCrawler

    env_file_path = os.path.join(root_dir, ".env.local")
    dotenv.load_dotenv(dotenv_path=env_file_path)
    token = os.getenv(key="GITHUB_ACCESS_TOKEN")
    print(token)
    crawler = GitHubCrawler(token)

    # Examples of different GitHub URL forms
    urls = [
        "https://github.com/ConsenSys/0x_audit_report_2018-07-23",
        "https://github.com/0xProject/0x-protocol-specification/blob/3.0/v3/v3-specification.md",
        "https://github.com/code-423n4/2022-05-alchemix",
        "https://github.com/code-423n4/2022-10-zksync-findings/issues/46",
        "https://github.com/code-423n4/2022-10-zksync/blob/456078b53a6d09636b84522ac8f3e8049e4e3af5/ethereum/contracts/bridge/L1ERC20Bridge.sol#L164-L169",
    ]
    cnt = 0
    for url in urls:
        try:
            data = crawler.fetch_data(url)
        except ValueError as e:
            print(f"Error: {e}")
            cnt += 1
