# STATISTICS ANALYSIS
## Descritpion
- Classify and analyze the data collected from **Code4rena**, **Consensys**, **OpenZeppelin**, and **Quantstamp**. The results include '**Analysis**' and '**Statistics**'. The statistics summarize the analyses and categorize them by company.
- Analyses include:
  - links
    - links in each report.
  - severity_count
    - Definition of severity varies from companies.
  - findings_details
    - For details, see blow
- Statistics include:
  - Number of projects.
  - Number and types of links in reports.
  - Number of severity count of issues in reports.
  - Frequency of languages refered in reports.
- Note:
  - Before having analyses, we should have projects and repos data crawled.
  - The "languages" data records only the file extensions referenced in the project. Therefore, the presence of ".js" does not necessarily indicate that the project was developed using JavaScript; it simply means that files with the ".js" extension were detected.

## Execution
### Command line arguements
  - platfrom (--platfrom, -p)
    - code4rena
    - consensys
    - openzeppelin
    - quantstamp
    - all
### Examples
```python=
# create Code4renaAnalyzer to analyze code4rena projects
python analyze.py -p code4rena

# create all analyzers to analyze data (4 analyzer listed above)
python analyze.py -p all  
```

## Analyses
### Data Storage
- **data\/<companiy name\>/analysis.json**
### Data Format
  - `projects`
    - `total`: int
      - The total number of projects.
    - `Website`:int
      - The number of project reports are presented in website.
    - `github`: int
      - The number of project reports that are presented using github.
    - `pdf`: int
      - The number of project reports that are presented in pdf.
  - `links`
    - `<project name\>`
      - `total`: int
        - The total number of links.
      - `github`: int
        - The number of github links, including issues.
      - `github_issue`: int
        - The number of github issues links.
      - `github_broken`: int
        - The number of broken github links.
      - `pdf`: int
        - The number of links to pdf files.
  - `severity_count`
      - `<Quantstmap project name>`
        - `high_risk`: int
        - `medium_risk`: int
        - `low_risk`: int
        - `informational`: int
        - `undetermined`: int
      - `<Openzeppelin project name>`
        - `critical_risk`: int
        - `high_risk`: int
        - `medium_risk`: int
        - `low_risk`: int
      - `<Consensys project name>`
        - `critical_risk`: int
        - `major_risk`: int
        - `medium_risk`: int
        - `minor_risk`: int
      - `<Code4rena project name>`
        - `high_risk`: int
        - `medium_risk`: int
        - `low_risk`: int
        - `low_risk_non_critical`: int
  - `findings_details`: list of dict
    - `project_name`: str
    - `issues`
      - `issue_title`
      - `severity`
      - `status`
        - acknowledged, fixed, mitigated, ...
    - `languages`
      - `Rust`: int
      - `Golang`: int
      - `Solidity`: int
      - `Circom`: int
      - `C`: int
      - `C++`: int
      - `Cadence`: int
      - `Typescript`: int
      - `Python`: int
      - `Java`: int
      - `Kotlin`: int
      - `Vyper`: int
      - `Scilla`: int
      - `TOML`: int
      - `N/A`: int
    - `timestamp`: str (YYYY-MM)


## Statistics
### Data Storage
- No storage. Just output from **statistics.py**

### Projects
- Descirption
  - The numbers of auditted projects of each company.
    - Wbsite: Reports that are presented in offcial sebsites.
    - Github: Reports that are presented in a github repo
    - Pdf: Reports that are presented in pdf.
- Analysis

|              | Total | Wesite | Github Repo | Pdf |
| ------------ | ----- | ------ | ----------- | --- |
| Quantstamp   | 360   | 211    | 0           | 149 |
| Consensys    | 158   | 137    | 20          | 1   |
| Openzeppelin | 225   | 225    | 0           | 0   |
| Code4rena    | 386   | 386    | 0           | 0   |

### Links
- Descirption
  - Links in the reports from each company. Reports may be presented in wesites, github repos, pdfs,
    - Github: Github Links
    - Github_issue: Github Issue links
    - Github_broken: Github links which are broken.
    - Pdf: Links to pdf files.
- Analysis

|              | Total  | Github | Github_issue | Github_broken | Pdf |
| ------------ | ------ | ------ | ------------ | ------------- | --- |
| Quantstamp   | 15611  | 1632   | 13           | 0             | 46  |
| Consensys    | 3021   | 1631   | 214          | 0             | 62  |
| Openzeppelin | 34597  | 27624  | 60           | 0             | 20  |
| Code4rena    | 101113 | 64943  | 40276        | 0             | 46  |

### Languages
- Description
  - The numbers for each language on each company represent how frequent they are mentioned in the reports.
- Analysis

|              | Solidity | Circom | Go  | Typescript | Rust | C | C++ | Vyper | Javascript | Cadence | Python | Kotlin | Java | Scilla | TOML |
| ------------ | -------- | ------ | --- | ---------- | ---- | - | --- | ----- | ---------- | ------- | ------ | ------ | ---- | ------ | ---- |
| Quantstamp   | 42973    | 200    | 794 | 5409       | 2384 | 0 | 6   | 43    | 3339       | 114     | 84     | 0      | 0    | 0      | 14   |
| Consensys    | 7375     | 0      | 215 | 679        | 0    | 1 | 0   | 22    | 233        | 0       | 33     | 0      | 0    | 0      | 0    |
| Openzeppelin | 52809    | 228    | 362 | 329        | 1341 | 0 | 0   | 32    | 98         | 0       | 22     | 0      | 0    | 0      | 3    |
| Code4rena    | 94541    | 0      | 1991| 289        | 1958 | 1 | 6   | 83    | 180        | 3       | 49     | 0      | 0    | 0      | 41   |

### Severity Count
- Description
  - The number of issues in the reports for each company, classified by severity as defined by each platform.
- Analysis

|              | Severity              | Count |
| ------------ | --------------------- | ----- |
| Quantstamp   | high_risk             | 366   |
|              | medium_risk           | 726   |
|              | low_risk              | 1643  |
|              | informational         | 1366  |
|              | undetermined          | 266   |
| Consensys    | critical_risk         | 92    |
|              | major_risk            | 243   |
|              | medium_risk           | 415   |
|              | minor_risk            | 545   |
| Openzeppelin | critical_risk         | 121   |
|              | high_risk             | 215   |
|              | medium_risk           | 591   |
|              | low_risk              | 1386  |
| Code4rena    | high_risk             | 1054  |
|              | medium_risk           | 2560  |
|              | low_risk              | 331   |
|              | low_risk_non_critical | 3035  |
