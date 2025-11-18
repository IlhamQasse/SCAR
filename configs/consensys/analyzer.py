from typing import TypedDict

ANALYSIS_DATA_PATH = "{root_dir}/data/consensys/analysis.json"
ANALYSIS_ERROR_PATH = "{root_dir}/data/consensys/analysis_errors.txt"


class SeverityCount(TypedDict):
    critical_risk: int
    major_risk: int
    medium_risk: int
    minor_risk: int


findings_status_type = {
    "fixed": "Fixed",
    "partially_addressed": "Partially Addressed",
    "acknowledged": "Acknowledged",
    "unverified_fix": "Unverified Fix",
    "won't_fix": "Won't Fix",
    "pending": "Pending",
    "unknown": "",
}


findings_severity_type = {
    "critical_risk": "critical",
    "major_risk": "major",
    "medium_risk": "medium",
    "minor_risk": "minor",
}


def init_severity_count() -> SeverityCount:
    return {
        "critical_risk": 0,
        "major_risk": 0,
        "medium_risk": 0,
        "minor_risk": 0,
    }
