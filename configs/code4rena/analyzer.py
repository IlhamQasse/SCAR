from enum import Enum
from typing import TypedDict

ANALYSIS_DATA_PATH = "{root_dir}/data/code4rena/analysis.json"
ANALYSIS_ERROR_PATH = "{root_dir}/data/code4rena/analysis_errors.txt"


class SeverityCount(TypedDict):
    high_risk: int
    medium_risk: int
    low_risk: int
    low_risk_non_critical: int


findings_severity_type = {
    "high_risk": "High Risk Findings",
    "medium_risk": "Medium Risk Findings",
    "low_risk": "Low Risk Findings",
    "low_risk_non_critical": "Low Risk and Non-Critical Issues",
}


def init_severity_count() -> SeverityCount:
    return {
        "high_risk": 0,
        "medium_risk": 0,
        "low_risk": 0,
        "low_risk_non_critical": 0,
    }
