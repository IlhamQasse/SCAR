import os
import json
from configs.base.types import (
    Platform,
    ProjectAnalysis,
    ProjectInfo,
    LinkInfo,
    init_link_info,
    LanguageInfo,
    SeverityCount,
)


platforms = [p.value.lower() for p in Platform.__members__.values()]
root_dir = os.path.dirname(__file__)


def get_statistics_data_paths_of_platfroms() -> dict[str, str]:
    statistics_data_paths = {}
    for platform in platforms:
        import_path = f"configs.{platform}.analyzer"
        var_name = "ANALYSIS_DATA_PATH"
        data_path = __import__(import_path, fromlist=[var_name])
        data_path = getattr(data_path, var_name)
        data_path = data_path.format(root_dir=root_dir)
        statistics_data_paths[platform] = data_path
    return statistics_data_paths


def get_finding_severity_types_of_platfroms() -> dict[str, str]:
    inding_severity_types = {}
    for platform in platforms:
        import_path = f"configs.{platform}.analyzer"
        var_name = "findings_severity_type"
        data_path = __import__(import_path, fromlist=[var_name])
        data_path = getattr(data_path, var_name)
        inding_severity_types[platform] = data_path
    return inding_severity_types


def get_analysis_data_of_platfrom(file_path: str) -> ProjectAnalysis:
    with open(file_path, "r") as file:
        return json.load(file)


def get_statistics_data_of_platfroms() -> dict[str, ProjectAnalysis]:

    statistics_data_paths = get_statistics_data_paths_of_platfroms()
    statistics_data = {}
    for platform, path in statistics_data_paths.items():
        if not os.path.exists(path):
            continue
        statistics_data[platform] = get_analysis_data_of_platfrom(path)
    return statistics_data


def generate_projects_info(data: dict[str, ProjectInfo]):
    """
    input data:
    {
        <platform>: ProjectInfo
    }
    """
    for platform, project_info in data.items():
        print(f"Platform: {platform.capitalize()}")
        for key, value in project_info.items():
            print(f" - {key.capitalize()}: {value}")
        print()


def generate_links_info(data: dict[str, dict[str, LinkInfo]]):
    """
    input data:
    {
        <platform>: {
            <project_name>: {
                <link>: <count>
            }
        }
    }
    """
    overal_link_info = {}
    for platform, link_info in data.items():
        total_link_info = init_link_info()
        for key, value in link_info.items():
            for k, v in value.items():
                total_link_info[k] += v
        overal_link_info[platform] = total_link_info

    for platform, link_info in overal_link_info.items():
        print(f"Platform: {platform.capitalize()}")
        for key, value in link_info.items():
            print(f" - {key.capitalize()}: {value}")
        print()


def generate_languages_info(data: dict[str, dict[str, LanguageInfo]]):
    """
    input data:
    {
        <platform>: {
            <project_name>: {
                <language>: <count>
            }
        }
    }
    """
    languages = {}
    for platform, language_info in data.items():
        overall_language_info = {}
        for _, info in language_info.items():
            for language, count in info.items():
                if language not in overall_language_info:
                    overall_language_info[language] = 0
                overall_language_info[language] += count
        languages[platform] = overall_language_info

    # generate total language info
    for platform, language_info in languages.items():
        print(f"Platform: {platform.capitalize()}")
        for key, value in language_info.items():
            print(f" - {key.capitalize()}: {value}")
        print()


def generate_severity_count(data: dict[str, dict[str, SeverityCount]]):
    """
    input data:
    {
        <platform>: {
            <project_name>: {
                <severity>: <count>
            }
        }
    }
    """
    for platform, finding_info in data.items():
        overall_finding_info = {}
        for _, info in finding_info.items():
            for severity, count in info.items():
                overall_finding_info[severity] = (
                    overall_finding_info.get(severity, 0) + count
                )
        print(f"Platform: {platform.capitalize()}")
        for key, value in overall_finding_info.items():
            print(f" - {key.capitalize()}: {value}")
        print()


if __name__ == "__main__":
    statistics_data = get_statistics_data_of_platfroms()
    project_infos = {
        platform: statistics_data[platform]["projects"] for platform in platforms
    }
    links_infos = {
        platform: statistics_data[platform]["links"] for platform in platforms
    }
    language_infos = {
        platform: {
            d["project_name"]: d["languages"]
            for d in statistics_data[platform]["findings_details"]
        }
        for platform in platforms
    }
    severity_count = {
        platform: statistics_data[platform]["severity_count"] for platform in platforms
    }

    print("============ Projects  Info =============")
    generate_projects_info(project_infos)
    print("=============  Links  Info ==============")
    generate_links_info(links_infos)
    print("============ Severity Count =============")
    generate_severity_count(severity_count)
    print("============ Languages Info =============")
    generate_languages_info(language_infos)
