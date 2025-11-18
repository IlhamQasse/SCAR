from typing import TypedDict

ANALYSIS_DATA_PATH = "{root_dir}/data/quantstamp/analysis.json"
ANALYSIS_ERROR_PATH = "{root_dir}/data/quantstamp/analysis_errors.txt"


class SeverityCount(TypedDict):
    high_risk: int
    medium_risk: int
    low_risk: int
    informational: int
    undetermined: int


findings_status_type = {
    "undetermined": "Undetermined",
    "fixed": "Fixed",
    "mitigated": "Mitigated",
    "acknowledged": "Acknowledged",
}

findings_severity_type = {
    "high_risk": "High",
    "medium_risk": "Medium",
    "low_risk": "Low",
    "informational": "Informational",
    "undetermined": "Undetermined",
}


def init_severity_count() -> SeverityCount:
    return {
        "high_risk": 0,
        "medium_risk": 0,
        "low_risk": 0,
        "informational": 0,
        "undetermined": 0,
    }
