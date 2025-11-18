from enum import Enum
from typing import TypedDict


class ReportFile(TypedDict):
    file_path: str
    report_name: str


class ReportLink(TypedDict):
    url: str
    hypertext: str


class Platform(Enum):
    Quantstamp = "Quantstamp"
    Consensys = "Consensys"
    OpenZeppelin = "OpenZeppelin"
    Code4rena = "Code4rena"


class CrawlerType(Enum):
    Report = "report"
    Project = "project"
    Repo = "repo"


# ================================
# type alias
ProjectName = str


class ProjectInfo(TypedDict):
    total: int
    github: int
    pdf: int


class LinkInfo(TypedDict):
    total: int = 0
    github: int = 0
    github_issue: int = 0
    github_broken: int = 0
    pdf: int = 0


class LanguageInfo(TypedDict):
    Solidity: int
    Golang: int
    Rust: int
    Vyper: int
    C: int
    Cpp: int
    Cadence: int
    Typescript: int
    Javascript: int
    Python: int
    Java: int
    Circom: int
    Kotlin: int
    Scilla: int
    TOML: int


class Issue(TypedDict):
    issue_title: str
    severity: str
    status: str


class FindingsDetail(TypedDict):
    project_name: str
    timestamp: str
    languages: LanguageInfo
    issues: list[Issue]


SeverityCount = dict[str, int]


class ProjectAnalysis(TypedDict):
    projects: ProjectInfo
    links: dict[str, LinkInfo]
    findings_details: list[FindingsDetail]
    severity_count: dict[str, int]


language_candidates = {
    r"\.sol\b": "Solidity",
    r"\.go\b": "Golang",
    r"\.rs\b": "Rust",
    r"\.vy\b": "Vyper",
    r"\.c\b": "C",
    r"\.cpp\b": "C++",
    r"\.cdc\b": "Cadence",
    r"\.ts\b": "Typescript",
    r"\.js\b": "Javascript",
    r"\.py\b": "Python",
    r"\.java\b": "Java",
    r"\.circom\b": "Circom",
    r"\.kt\b": "Kotlin",
    r"\.scilla\b": "Scilla",
    r"\.toml\b": "TOML",
}


def init_link_info(total: int = 0) -> LinkInfo:
    return LinkInfo(total=total, github=0, github_issue=0, github_broken=0, pdf=0)


# ================================
