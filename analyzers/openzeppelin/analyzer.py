from tqdm import tqdm
from configs.base.types import FindingsDetail, Issue, ProjectName
from configs.openzeppelin.analyzer import (
    ANALYSIS_DATA_PATH,
    ANALYSIS_ERROR_PATH,
    findings_severity_type,
    init_severity_count,
    findings_status_type,
    SeverityCount,
)
from configs.openzeppelin.report import REPORT_DATA_PATH
from configs.openzeppelin.project import PROJECT_LIST_PATH
from helpers.report import create_tqdm_title, get_languages_of_report
from helpers.date import openzeppelin_date_convertor
from ..base.analyzer import AnalyzerBase, AnalyzerConfig
from .helper import get_issues_from_report_data_details


class Analyzer(AnalyzerBase):
    def __init__(self, root_dir: str):

        config = AnalyzerConfig(
            root_dir=root_dir,
            project_list_path=PROJECT_LIST_PATH,
            report_data_path=REPORT_DATA_PATH,
            analysis_data_path=ANALYSIS_DATA_PATH,
            analysis_error_path=ANALYSIS_ERROR_PATH,
        )
        super().__init__(config)

    def get_severity_count_of_reports(self) -> dict[ProjectName, SeverityCount]:
        """
        compile risks level of reports, 4 level involved:
        - critical_risk: int,
        - high_risk: int,
        - medium_risk: int,
        - low_risk: int,
        """
        reports = self.get_reports_file_paths()
        findings_info = {}
        title = create_tqdm_title("Issues info of reports")
        for report in tqdm(reports, desc=title):
            report_name = report.split("/")[-1].split(".")[0]
            report_data = self.load_json_file(report)
            analysis = init_severity_count()
            for detail in report_data["details"]:
                title = detail["title"].lower()
                for key, value in findings_severity_type.items():
                    if value.lower() in title:
                        analysis[key] += len(detail["content"])
            findings_info[report_name] = analysis
        return findings_info

    def get_findings_details_of_reports(
        self,
    ) -> list[FindingsDetail]:
        """
        return value of details_of_all_projects:
        [
            {
                "project_name": str,
                "timestamp": str,
                "languages": dict[str, int],
                "issues": [
                    {
                        "issue_title": str,
                        "severity": str,
                        "status": findings_status_type
                    },
                    ...
                ]
            },
            ...
        ]
        """
        details_of_all_projects = []
        reports = self.get_reports_file_paths()
        title = create_tqdm_title("Findings details of reports")
        for report in tqdm(reports, desc=title):
            detail_of_cur_project = {}
            # get findings details of each
            report_data = self.load_json_file(report)

            # project name
            project_name = self.get_project_name_from_path(report)
            detail_of_cur_project["project_name"] = project_name

            # languages
            languages = get_languages_of_report(report_data)
            detail_of_cur_project["languages"] = languages

            # some details don't contain issues.
            issues_infos = []
            issues = get_issues_from_report_data_details(report_data["details"])
            issues_infos += self.get_infos_of_issues(issues)
            detail_of_cur_project["issues"] = issues_infos
            details_of_all_projects.append(detail_of_cur_project)

        # add timestamp to details_of_all_projects
        project_list = self.load_project_list()
        for project in details_of_all_projects:
            project_name = project["project_name"]
            for project_info in project_list:
                if project_info["project_name"] == project_name:
                    date = openzeppelin_date_convertor(project_info["date"])
                    project["timestamp"] = date
                    break
        return details_of_all_projects

    def get_infos_of_issues(self, issues: list[dict]) -> list[Issue]:
        """
        input issues:
        [
            {
                "subtitle": str,
                "content": [...]
                "severity": str,
            }, ...
        ],
        """
        issues_infos = []
        for issue in issues:
            subtitle = issue["subtitle"].lower()
            issue_info = {"issue_title": subtitle, "severity": issue["severity"]}
            issue_content = issue["content"]
            if not issue_content:
                continue

            # status of a issue is in update
            # update usually is the last element in content
            update = issue_content[-1]
            if not isinstance(update, str):
                continue

            for status, value in findings_status_type.items():
                # value not in lowercase, so resolved and partially_resolved can be distinguished
                update = update.split("Update: ")[-1]
                if update.startswith(value):
                    issue_info["status"] = status
                    break

            # if status is not found, set it to unknown
            if "status" not in issue_info:
                issue_info["status"] = "unknown"
            issues_infos.append(issue_info)
        return issues_infos

    def analyze(self):
        print("Analyzing OpenZeppelin projects...")
        projects_info = self.get_overall_projects_info()
        links_info = self.get_links_info_of_reports()
        severity_count = self.get_severity_count_of_reports()
        findings_details = self.get_findings_details_of_reports()
        analysis = {
            "projects": projects_info,
            "links": links_info,
            "severity_count": severity_count,
            "findings_details": findings_details,
        }
        self.save_analysis_data(analysis)
