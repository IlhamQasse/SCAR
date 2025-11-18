import base64
import re
import requests
from github import Github
from configs.base.github import (
    GITHUB_BASE_URL,
    GITHUB_BASE__API_URL,
    GITHUB_URL_PATTERN,
)


class GitHubCrawler:
    def __init__(self, token: str):
        self.token = token
        self.base_url = GITHUB_BASE_URL
        self.base_api_url = GITHUB_BASE__API_URL
        self.headers = {"Authorization": f"token {token}"}
        self.url_pattern = GITHUB_URL_PATTERN

    def parse_url(self, url: str) -> dict:
        if not url.startswith(self.base_url):
            raise ValueError("Not a GitHub URL")

        if url.endswith(".pdf"):
            raise ValueError("PDF files are not supported")

        match = re.match(self.url_pattern, url)

        if not match:
            raise ValueError("Invalid GitHub URL")

        # Extract components from the match object
        components = match.groupdict()

        # Determine the resource type based on captured groups
        if components["issue_number"]:
            resource_type = "issue"
        elif "blob" in url:
            resource_type = "file"
        else:
            # if type == tree, also a repository
            resource_type = "repository"

        # Prepare output with consistent key 'type'
        parsed_url = {
            "username": components["username"],
            "repository": components["repo"],
            "branch": components.get("branch"),
            "file_path": components.get("path"),
            "start_line": components.get("start_line"),
            "end_line": components.get("end_line"),
            "issue_number": components.get("issue_number"),
            "type": resource_type,  # Adding 'type' for clarity and consistency
        }

        # Cleaning up the dictionary: remove None values
        return {k: v for k, v in parsed_url.items() if v is not None}

    def create_request_url(self, parsed_url: dict) -> str | None:
        username = parsed_url.get("username")
        repo = parsed_url.get("repository")

        if parsed_url["type"] == "file":
            branch = parsed_url.get("branch")
            file_path = parsed_url.get("file_path")
            return f"{self.base_api_url}/{username}/{repo}/contents/{file_path}?ref={branch}"

        elif parsed_url["type"] == "issue":
            issue_number = parsed_url.get("issue_number")
            return f"{self.base_api_url}/{username}/{repo}/issues/{issue_number}"

        return None  # Return None if type does not require a specific API URL

    def parse_file_content(self, response: dict, type: str):
        data = {}
        if type == "file":
            data["content"] = base64.b64decode(response["content"]).decode("utf-8")
            data["type"] = type
        else:
            data = response
            data["type"] = type
        return data

    def fetch_repository(self, repo: str):
        print(f"Fetching repository {repo}")
        g = Github(self.token)
        repo = g.get_repo(repo)
        contents = repo.get_contents("")

        all_files = {}

        while contents:
            file_content = contents.pop(0)
            if not file_content.path.endswith(".sol"):
                continue
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            elif file_content.type == "file":
                # Optionally decode content if you want the file's content
                data = base64.b64decode(file_content.content).decode("utf-8")
                all_files[file_content.path] = data
                print(f"Fetched {file_content.path}")

        return all_files

    def fetch_data(self, url: str) -> dict | None:

        # If the URL is a repository URL, fetch all files in the repository
        parsed_url = self.parse_url(url)
        if parsed_url["type"] == "repository":
            res = self.fetch_repository(
                f"{parsed_url['username']}/{parsed_url['repository']}"
            )
            res["type"] = "repository"
            return res

        # Create the API URL
        # Parse the URL in order to make api request
        api_url = self.create_request_url(parsed_url)
        if api_url is None:
            raise ValueError("Invalid URL")

        # Fetch data from the API
        response = requests.get(api_url, headers=self.headers)
        if response.status_code != 200:
            raise ValueError("Failed to fetch data")

        # parse the response
        return self.parse_file_content(response.json(), parsed_url["type"])
