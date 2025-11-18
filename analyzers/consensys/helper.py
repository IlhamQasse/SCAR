def get_issues_from_report_data_details(details: dict) -> list[dict]:
    """
    return a list of issues from report_data["details"]
    """
    for detail in details:
        title = detail["title"].lower()
        if "findings" not in title and "issues" not in title:
            continue
        return detail["content"]
    return []
