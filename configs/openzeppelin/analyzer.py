from typing import TypedDict

ANALYSIS_DATA_PATH = "{root_dir}/data/openzeppelin/analysis.json"
ANALYSIS_ERROR_PATH = "{root_dir}/data/openzeppelin/analysis_errors.txt"


class SeverityCount(TypedDict):
    critical_risk: int
    high_risk: int
    medium_risk: int
    low_risk: int


findings_status_type = {
    "resolved": "Resolved",
    "fixed": "Fixed",
    "partially_resolved": "Partially resolved",
    "acknowledged": "Acknowledged",
    "unknown": "",
}

findings_severity_type = {
    "critical_risk": "Critical Severity",
    "high_risk": "High Severity",
    "medium_risk": "Medium Severity",
    "low_risk": "Low Severity",
}


def init_severity_count() -> SeverityCount:
    return {
        "critical_risk": 0,
        "high_risk": 0,
        "medium_risk": 0,
        "low_risk": 0,
    }
