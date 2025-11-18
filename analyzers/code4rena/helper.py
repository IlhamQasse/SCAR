from configs.code4rena.analyzer import findings_severity_type


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
        for _, value in findings_severity_type.items():
            if value in detail["title"]:
                for content in detail["content"]:
                    content["severity"] = value
                    issues.append(content)
    return issues
