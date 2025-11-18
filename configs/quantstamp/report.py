from enum import Enum


REPORT_DATA_PATH = "{root_dir}/data/quantstamp/reports/{name}"
REPORT_ERROR_LOG_PATH = "{root_dir}/data/quantstamp/errors/{name}.txt"
# data storage
REPORT_SECTION_XPATH = "/html/body/div/div/div/div[2]/section[{number}]"
REPORT_CONTAINER_XPATH = "/html/body/div/div/div/div[2]"
REPORT_EXECUTIVE_SUMMARY_XPATH = (
    REPORT_SECTION_XPATH.format(number=1) + "/div/div[{number}]"
)
REPORT_SUMMARY_OF_FINDINGS_XPATH = REPORT_SECTION_XPATH.format(number=2)

AUDIT_INFO_COLUMNS = [
    "Type",
    "Timeline",
    "Language",
    "Methods",
    "Specification",
    "Source Code",
    "Auditors",
]

AUDIT_SUMMARY_COLUMNS = [
    "Documentation quality",
    "Test quality",
    "Total Findings",
    "High severity findings",
    "Medium severity findings",
    "Low severity findings",
    "Undetermined severity findings",
    "Informational findings",
]

SUMMARY_OF_FINGINDS_COLUMNS = ["ID", "Description", "Severity", "Status"]

VALID_KEYS_IN_FINDINGS = [
    "File(s) affected",
    "Description",
    "Recommendation",
    "Exploit Scenario",
]


class REPORT_SECTION_ID(Enum):
    EXECUTIVE_SUMMARY = "executive-summary"
    SUMMARY_OF_FINDINGS = "summary-of-findings"
    ASSESSMENT_BREAKDOWN = "assessment-breakdown"
    SCOPE = "scope"
    FINDINGS = "findings"
    DEFINITIONS = "definitions"
    CODE_DOCUMENTATION = "code-documentation"
    ADHERENCE_TO_BEST_PRACTICES = "adherence-to-best-practices"
    APPENDIX = "appendix"
    TOOLSET = "toolset"
    AUTOMATED_ANALYSIS = "automated-analysis"
    CHANGELOG = "changelog"
    TEST_SUITE_RESULTS = "test-suite-results"
    CODE_COVERAGE = "code-coverage"
