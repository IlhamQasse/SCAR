from tqdm import tqdm
from configs.base.types import FindingsDetail, ProjectName
from configs.quantstamp.analyzer import (
    ANALYSIS_DATA_PATH,
    ANALYSIS_ERROR_PATH,
    findings_severity_type,
    init_severity_count,
    SeverityCount,
)
from configs.quantstamp.report import REPORT_DATA_PATH
from configs.quantstamp.project import PROJECT_LIST_PATH
from helpers.report import create_tqdm_title, get_languages_of_report
from helpers.date import quantstamp_date_convertor
from ..base.analyzer import AnalyzerBase, AnalyzerConfig


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
        compile risks level of reports, 5 level involved:
        - "high_risk": int,
        - "medium_risk": int,
        - "low_risk": int,
        - "informational": int
        - "undetermined": int,
        """
        reports = self.get_reports_file_paths()
        findings_info = {}
        title = create_tqdm_title("Findings info of reports")
        for report in tqdm(reports, desc=title):
            report_name = report.split("/")[-1].split(".")[0]
            report_data = self.load_json_file(report)
            analysis = init_severity_count()
            for data in report_data["data"]:
                if data["title"] != "summary-of-findings":
                    continue
                for detail in data["details"]:
                    for key, value in findings_severity_type.items():
                        if value == detail["severity"]:
                            analysis[key] += 1
            findings_info[report_name] = analysis
        return findings_info

    def get_findings_details_of_reports(self) -> list[FindingsDetail]:
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

            # some details don't contain issues.
            issues = []
            for detail in report_data["data"]:
                if detail["title"] != "summary-of-findings":
                    continue
                for issue in detail["details"]:
                    issue_info = {
                        "issue_title": issue["description"],
                        "severity": issue["severity"],
                        "status": issue["status"],
                    }
                    issues.append(issue_info)
            detail_of_cur_project["issues"] = issues

            # languages
            languages = get_languages_of_report(report_data)
            detail_of_cur_project["languages"] = languages
            details_of_all_projects.append(detail_of_cur_project)

        # add timestamp to details_of_all_projects
        project_list = self.load_project_list()
        for detail in details_of_all_projects:
            for project in project_list:
                if project["project_name"] == detail["project_name"]:
                    # timestamp
                    date = quantstamp_date_convertor(project["date"])
                    detail["timestamp"] = date
                    break
            if "timestamp" not in detail:
                detail["timestamp"] = "unknown"
            if "languages" not in detail:
                detail["languages"] = {}
        return details_of_all_projects

    def analyze(self):
        print("Analyzing Quantstamp projects...")
        projects_info = self.get_overall_projects_info()
        links_info = self.get_links_info_of_reports()
        severity_count = self.get_severity_count_of_reports()
        findgins_details = self.get_findings_details_of_reports()
        analysis = {
            "projects": projects_info,
            "links": links_info,
            "severity_count": severity_count,
            "findings_details": findgins_details,
        }
        self.save_analysis_data(analysis)
