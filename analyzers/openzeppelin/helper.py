from configs.openzeppelin.analyzer import findings_severity_type


def get_issues_from_report_data_details(details: dict) -> list[dict]:
    """
    return a list of issues from report_data["details"]
    Note:
        we can not know the severity from detail["content"],
        so add new column "severity" to each issue
    """
    issues = []
    # if a key in title, then there are issues in this detail.
    # Keys are values of severity
    for detail in details:
        title = detail["title"].lower()
        for _, value in findings_severity_type.items():
            if value.lower() in title:
                for content in detail["content"]:
                    content["severity"] = value.lower()
                    issues.append(content)
    return issues
