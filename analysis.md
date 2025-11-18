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
  | Quantstamp   | 228   | 82     | 0           | 146 |
  | Consensys    | 136   | 115    | 20          | 1   |
  | Openzeppelin | 222   | 222    | 0           | 0   |
  | Code4rena    | 287   | 287    | 0           | 0   |

### Links
- Descirption
  - Links in the reports from each company. Reports may be presented in wesites, github repos, pdfs,
    - Github: Github Links
    - Github_issue: Github Issue links
    - Github_broken: Github links which are broken.
    - Pdf: Links to pdf files.
- Analysis
  |              | Total | Github | Github_issue | Github_broken | Pdf |
  | ------------ | ----- | ------ | ------------ | ------------- | --- |
  | Quantstamp   | 3809  | 385    | 3            | 0             | 11  |
  | Consensys    | 2524  | 1341   | 211          | 0             | 62  |
  | Openzeppelin | 9323  | 7250   | 21           | 0             | 0   |
  | Code4rena    | 73386 | 48355  | 30834        | 0             | 38  |

### Languages
- Description
  - The numbers for each language on each company represent how frequent they are mentioned in the reports.
- Analysis
  
  |              | Solidity | Circom | Go  | Typescript | Rust | C    | C++ | Vyper | Javascript | Cadence | Python | Kotlin | Java | Scilla | TOML |
  | ------------ | -------- | ------ | --- | ---------- | ---- | :--- | --- | ----- | ---------- | ------- | ------ | ------ | ---- | ------ | ---- |
  | Quantstamp   | 13813    | 103    | 2   | 952        | 0    | 0    | 2   | 0     | 376        | 2       | 32     | 0      | 0    | 0      | 6    |
  | Consensys    | 6127     | 0      | 215 | 461        | 0    | 1    | 0   | 22    | 193        | 0       | 33     | 0      | 0    | 0      | 0    |
  | Openzeppelin | 14452    | 0      | 183 | 224        | 376  | 0    | 0   | 0     | 4          | 0       | 0      | 0      | 0    | 0      | 3    |
  | Code4rena    | 78512    | 0      | 27  | 262        | 690  | 1    | 6   | 83    | 147        | 0       | 33     | 0      | 0    | 0      | 29   |

### Severity Count
- Description
  - The number of issues in the reports for each company, classified by severity as defined by each platform.
- Analysis
  |              | Severity              | Count |
  | ------------ | --------------------- | ----- |
  | Quantstamp   | high_risk             | 134   |
  |              | medium_risk           | 232   |
  |              | low_risk              | 579   |
  |              | informational         | 425   |
  |              | undetermined          | 98    |
  | Consensys    | critical_risk         | 80    |
  |              | major_risk            | 208   |
  |              | medium_risk           | 342   |
  |              | minor_risk            | 418   |
  | Openzeppelin | critical_risk         | 18    |
  |              | high_risk             | 47    |
  |              | medium_risk           | 150   |
  |              | low_risk              | 346   |
  | Code4rena    | high_risk             | 840   |
  |              | medium_risk           | 2005  |
  |              | low_risk              | 332   |
  |              | low_risk_non_critical | 2176  |