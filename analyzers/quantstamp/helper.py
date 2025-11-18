from configs.quantstamp.analyzer import findings_severity_type


def get_issues_from_report_data_details(details: dict) -> list[dict]:
    """
    return a list of issues from report_data["data"]
    """
    issues = []
    for data in details:
        if data["title"] != "findings":
            continue
        for detail in data["details"]:
            for _, value in findings_severity_type.items():
                if value == detail["severity"]:
                    issues.append(detail)

    return issues
