import re
import requests
from configs.base.types import ReportLink, init_link_info, LinkInfo, language_candidates


def get_all_links_from_report(json_data: dict | list) -> list[ReportLink]:
    links = []
    # If the data is a list, iterate over each item
    if isinstance(json_data, list):
        for item in json_data:
            links.extend(get_all_links_from_report(item))

    # If the data is a dictionary, process each key-value pair
    elif isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == "links" and isinstance(value, list):
                # Extract each link's URL from the list of link dictionaries
                links += value
            else:
                # Recursively search for more links
                links.extend(get_all_links_from_report(value))
    return links


def is_vaild_github_url(url: str):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def analyze_links_info(
    links: list[ReportLink], check_broken: bool = False
) -> dict[str, int]:
    """
    links: list of ReportLink
    check_broken: boolean to check if the link is broken, default is False
    """
    github_url_base = "https://github.com"
    info: LinkInfo = init_link_info(len(links))
    for link in links:
        url = link.get("url", "")

        # Check if the URL is a GitHub link
        if url.startswith(github_url_base):
            info["github"] += 1
            if check_broken and not is_vaild_github_url(url):
                info["github_broken"] += 1
            elif "issues/" in url:
                info["github_issue"] += 1

        # Check if the URL is a PDF
        if url.endswith(".pdf"):
            info["pdf"] += 1
    return info


# Function to count language mentions based on patterns
def get_languages_from_project_url(url: str) -> dict[str, int]:
    languages = {}

    # Send a GET request to retrieve the page content
    res = requests.get(url)
    if res.ok:
        page_content = res.text

        # Search for each file extension using regular expressions
        for pattern, lang_name in language_candidates.items():
            matches = re.findall(pattern, page_content)
            if len(matches) > 0:
                languages[lang_name] = 1
    else:
        print(f"Error: {res.status_code}")

    return languages


# def get_languages_of_report(report: dict) -> dict[str, int]:
#    """
#    matching the language pattern in the issue content
#    """
#    languages = {}

#    # turn issue into string
#    report_str = str(report)

#    # Search for each file extension using regular expressions
#    for pattern, lang_name in language_candidates.items():
#        matches = re.findall(pattern, report_str)
#        if len(matches) > 0:
#            languages[lang_name] = 1
#    return languages


def get_languages_of_report(report: dict) -> dict[str, int]:
    """
    Match the language pattern in the issue content.
    """
    languages = {}

    # Convert issue to string
    report_str = str(report)

    # Extract URLs from the report
    urls = re.findall(r"https?://[^\s]+", report_str)

    # Search for each file extension using regular expressions
    for pattern, lang_name in language_candidates.items():
        # Check file extensions in the URLs
        for url in urls:
            file_path = extract_file_path_from_url(url)
            if re.search(pattern, file_path):
                languages[lang_name] = languages.get(lang_name, 0) + 1

        # Check file extensions in the report content
        matches = re.findall(pattern, report_str)
        languages[lang_name] = languages.get(lang_name, 0) + len(matches)

    return languages


def create_tqdm_title(title: str) -> str:
    return f"\033[94m[{title}]\033[0m"


def extract_file_path_from_url(url: str) -> str:
    """
    Extract the file path from a GitHub URL.
    """
    match = re.search(r"github\.com/.+/.+/blob/.+/(.+)#", url)
    if match:
        return match.group(1)
    return ""
