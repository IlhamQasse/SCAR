# Audit Report Crawlers
## Descritpion
- Collect audit reports from **Code4rena**, **Consensys**, **OpenZeppelin**, and **Quantstamp**.
- For the data, we have
  - Projects.
    - List of audited projects.
  - Reports
  - Repos
    - Codebase within GitHub commit histories, which can include a single file or the entire repository.
- Note:
  - Repo data is from provided GitHub links in reports. Before using the repo crawlers, please ensure report data exists.
  - Don't forget to place the gitHub access token in `.env.local`.
    ```env=
    GITHUB_ACCESS_TOKEN=<TOKEN FROM DEVELOPER SETTING\>
    ```
## Execution
Every time we create a report scaper to crawl reports on a platform, we should ensure that a porject list of the platfrom exists.
### Command line arguements
  - platfrom (--platfrom, -p)
    - code4rena
    - consensys
    - openzeppelin
    - quantstamp
    - all
  - type (--type, -t)
    - project
    - report
    - repo
### Examples
```python=
# create Code4renaProjectCrawler to crawl project list
python crawl.py -t project -p code4rena

# create Code4renaProjectCrawler to crawl repo data
python crawl.py -t repo -p code4rena

# create all crawlers to crawl report data (4 crawlers listed above)
python crawl.py -t report -p all
```


## Quantstamp
### Description
- [Schema flow](https://dbdiagram.io/d/Quantstamp-660f7b7a03593b6b613d79b6)
- [Audit Reports](https://certificate.quantstamp.com/)

### Data Storage
  - projects.json
    - `project_name`: name of the project
    - `category`: type of the project, such as defi, oracle, ...
    - `ecosystem`: chain deployed on
    - `language`: language used in the project
    - `date`: update date
    - `report_link`: link of report 
  - reports (folder)
    - <PROJECT NAME\>.json
  - repos (folder)
    - <PROJECT NAME\>
      - url (base64 encoded)
### Data Format
Quantstamp audit reports are stored in a structured JSON format. Each report is divided into multiple sections, each represented as a object under `data` list. Here's a brief overview of the data format for the first set of sections:

-`data`: list of each section objects
- #### executive_summary
  - `title`: `executive-summary`
  - `description`: A brief summary of the audit.
  - `details`: list
    - `key`: str
    - `value`: list
  - `codes`: Any relevant code snippets, which are wrapped in a code tag.
- #### summary_of_findings
  - `title`: `summary-of-findings`
  - `details`: A list of objects, each representing a specific issue found during the audit. Each object `includes`:
    - `id`: The unique identifier of the issue.
    - `description`: A description of the issue.
    - `severity`: The severity of the issue, which can be high, medium, or low.
    - `status`: The status of the issue, which can be Fixed, Acknowledged, etc.
  - `description`: A description of the project that was audited.
  - `links`: An array of link objects
  - `codes`: Any relevant code snippets, which are wrapped in a code tag.
- #### assessment_breakdown
  - `title`: `assessment-breakdown`
  - `description`: A breakdown of the assessment.
  - `disclaimer`: list of disclaimer
  - `issue`: List of issues
  - `methodology`: list of methodology (recursively)
  - `codes`: Any relevant code snippets, which are wrapped in a code tag.
  - `links`: An array of link objects
- #### scope
  - `title`: `scope`
  - `description`: A description of the scope of the audit, typically indicating which files or directories were included.
  - `Files Included`: A list of files or directories that were included from the audit.
  - `Files Excluded`: A list of files or directories that were excluded from the audit.
  - `codes`: Any relevant code snippets, which are wrapped in a code tag.
  - `links`: An array of link objects
- #### findings
  - `title`: `findings`
  - `details`
    - `title`: title of the issue
    - `severity`: The severity of the issue, which can be high, medium, or low.
    - `status`: The status of the issue, which can be Fixed, Acknowledged, etc.
    - `update`: update for current status
    - `content`: dict
      - `exploit scenario`, `description`,  `file(s) affected`, `recommendation`: key of content
        - `content`: content in the issue, can be description or solution.
        - `codes`: Any relevant code snippets, which are wrapped in a code tag.
  - `links`: An array of link objects
- #### definitions
  - `title`: `definitions`
  - `details`: list of object
    - `title`: "High severity", "Medium severity", and so on.
    - `content`: description of the severity.
- #### code_documentation
  - `title`: `code-documentation`
  - `details`: A summary of the code documentation, can be a nested list.
  - `codes`: Any relevant code snippets, which are wrapped in a code tag.
  - `links`: An array of link objects
- #### adherence_to_best_practices
  - `title`: `adherence-to-best-practices`
  - `description`: A summary of the project's adherence to best practices, can be a nested list..
  - `codes`: Any relevant code snippets, which are wrapped in a code tag.
  - `links`: An array of link objects
- #### appendix
  - `title`: `appendix`
  - `details`: list of objects
    - `title`: Any additional information or appendices, can be "File Signatures", Contracts, ...
    - `content`: content subject to the title.
  - `codes`: Any relevant code snippets, which are wrapped in a code tag.
  - `links`: An array of link objects
- #### automated_analysis
  - `title`: `automated-analysis`
  - `details`: list of objects
    - `title`: Any additional information or appendices, can be "Slither", or some other tools
    - `content`: content subject to the title.
  - `codes`: Any relevant code snippets, which are wrapped in a code tag.
  - `links`: An array of link objects
- #### changelog
  - `title`: `changelog`
  - `details`: list of strings or dicts
  - `links`: An array of link objects
- #### test_suite_results
  - `title`: `test-suite-results`
  - `description`: Results from the test suite.
  - `code_block`: code for execution results, or some commands.
  - `codes`: Any relevant code snippets, which are wrapped in a code tag.
  - `links`: An array of link objects
- #### code_coverage
  - `title`: `code-coverage`
  - `description`: Code coverage of testing, sometimes may contain the result of testing, sometimes just `description`.
  - `codes`: Any relevant code snippets, which are wrapped in a code tag.
  - `details`: 
    - `column`: list of table head.
    - `row`: list of table data.
  - `links`: An array of link objects
- #### toolset
  - `title`: `toolset`
  - `details`: list of objects
    - `title`: most of the time is "Tool Setup"
    - `content`: tool name
  - `description`: how to install the tools
  - `codes`: Any relevant code snippets, which are wrapped in a code tag.
  - `links`: An array of link objects
  
Each section in a Quantstamp report is handled by a corresponding method in the report.py file in the quantstamp directory. For example, the handle_summary_of_findings method handles the summary_of_findings section, and the handle_scope method handles the scope section. These methods parse the raw data and format it according to the structures described above.

Please note that not all sections may be present in every report, as the contents can vary based on the specifics of the audit. Each section should follow the same general format, but the specific properties included in each section will depend on the content of the section itself.
## Openzeppelin
### Description
- [Schema flow](https://dbdiagram.io/d/Openzeppelin-660f807e03593b6b613dc986)
- [Audit Reports](https://blog.openzeppelin.com/tag/security-audits)
### Data Storage
- projects.json
  - `project_name`: project's name,
  - `description`: description of the project,
  - `report_link`: report link,
  - `related_tags`: tags about the project topic
  - `date`: "MARCH 21, 2024"
- reports (folder)
  - <PROJECT NAME\>.json
- repos (folder)
  - <PROJECT NAME\>
    - url (base64 encoded)
### Data format
The provided JSON data represents a section of a report. Each section is an object within an array.
Each section object has the following properties:

#### Each section:
- `details`
  - `title`:  A string that represents the title of the section.
  - `content`:  An array of the subsections
    - `subtitle`: A string that represents the title of the subsection.If no subtitle is found, this is set to "subtitle_not_found".
    - `content`: An array of strings or objects that represents the actual content. Each string is a separate paragraph.
    - `blockquote`: An array that would contain any quoted text. In this excerpt, it's always empty.
    - `links`: An array of link objects. Each link object has the following properties:
      - `hypertext`: A string that represents the text of the hyperlink.
      - `url`: A string that represents the URL of the hyperlink.
    - `codes`: An array of strings that represents the texts wrapped by code tags.

Please note that the `links`, `blockquote`, and `codes` arrays can be empty, indicating that there are no links, quotes, or code snippets associated with the content.

## Consensys
### Description
- [schema flow](https://dbdiagram.io/d/Consensys-660f821403593b6b613de26e)
- [Audit Report](https://consensys.io/diligence/audits/)
### Data Storage
- projects.json
  - `project_name`: project's name,
  - `report_link`: report link,
  - `delivery_date`:  the date of the project delivered
- reports (folder)
  - <PROJECT NAME\>.json
- repos (folder)
  - <PROJECT NAME\>
    - url (base64 encoded)
### Data format
The provided JSON data represents a report. The report is an object with a `details` property, which is an array of section objects. Each section object has the following properties:

#### Non findings section:
- `details`
  - `title`: A string that represents the title of the section.
  - `content`: An array of subsection objects. Each content object has the following properties:
    - `subtitle`: A string that represents the subtitle of the content. If no subtitle is found, this is set to "subtitle_not_found".
    - `content`: An array of strings that represents the actual content. Each string is a separate paragraph.
    - `links`: An array of link objects. Each link object has the following properties:
      - `hypertext`: A string that represents the text of the hyperlink.
      - `url`: A string that represents the URL of the hyperlink.
    - `codes`: An array of strings that represents the texts wrapped by code tags.
 #### Findings seciton:
 - `details`
  - `title`: A string that represents the title of the section.
  - `content`: An array of subsection objects. Each content object has the following properties:
    - `subtitle`: A string that represents the subtitle of the content. If no subtitle is found, this is set to "subtitle_not_found".
    - `content`: An array of smsection objects. Each content object has the following properties:
      - `smtitle`: small title of "Resolution", "Description", "Recommendation", and some others.
      - `content`: An array of strings or objects that represents the actual content. Each string or objects is a separate paragraph.
      - `links`: An array of link objects. Each link object has the following properties:
        - `hypertext`: A string that represents the text of the hyperlink.
        - `url`: A string that represents the URL of the hyperlink.
      - `codes`: An array of strings that represents the texts wrapped by code tags.

Please note that the `links` and `codes` arrays can be empty, indicating that there are no links or code snippets associated with the content.

The data is nested, and each level of nesting is represented by an array or object. The structure allows for complex reports with multiple sections and multiple pieces of content within each section.

## Code4rena
### Descritpion
- [Schema flow](https://dbdiagram.io/d/Code4rena-66138b0803593b6b616e2733)
- [Audit Reports](https://code4rena.com/reports)
### Data Storage
- projects.json
  - `project_name`: project's name,
  - `report_link`: report link,
  - `period`:  the date the contest lasted
  - `date`: final report updated date
- reports (folder)
  - <PROJECT NAME\>.json
- repos (folder)
  - <PROJECT NAME\>
    - url (base64 encoded)
### Data format
The provided JSON data represents a report. The report is an object with a `details` property, which is an array of section objects. Each section object has the following properties:

#### Section without h3 tags:
- `details`
  - `title`: A string that represents the title of the section.
  - `content`: An array of subsection objects. Each content object has the following properties:
    - `subtitle`: A string that represents the subtitle of the content. If no subtitle is found, this is set to "subtitle_not_found".
    - `content`: An array of strings or objects that represents the actual content. Each string is a separate paragraph.
    - `links`: An array of link objects. Each link object has the following properties:
      - `hypertext`: A string that represents the text of the hyperlink.
      - `url`: A string that represents the URL of the hyperlink.
    - `codes`: An array of strings that represents the texts wrapped by code tags.
    - `blockquotes`: An array of strings that represents the texts wrapped by blockquote tags.
#### Section with h3 tags:
- `details`
  - `title`: A string that represents the title of the section.
  - `content`: An array of subsection objects . Each content object has the following properties:
    - `subtitle`: A string that represents the subtitle of the content. If no subtitle is found, this is set to "subtitle_not_found".
    - `content`: An array of smsection objects. Each content object has the following properties:
      - `smtitle`: small title of "Resolution", "Description", "Recommendation", and some others.
      - `content`: An array of strings or objects that represents the actual content. Each string or objects is a separate paragraph.
      - `links`: An array of link objects. Each link object has the following properties:
        - `hypertext`: A string that represents the text of the hyperlink.
        - `url`: A string that represents the URL of the hyperlink.
      - `codes`: An array of strings that represents the texts wrapped by code tags.
      - `blockquotes`: An array of strings that represents the texts wrapped by blockquote tags.




## Note for all
The list items using "ul" or "ol" tags are represented in dict as the following example:
```
- "MAX_ESCAPE_TIP_STRK = 1 STRK which limits the result of multiplying tip * L2_GAS.max_amount.",
- "MAX_ESCAPE_MAX_FEE_STRK = 50 STRK which limits the sum of all of the following:",
  - "L1_GAS.max_price_per_unit * L1_GAS.max_amount,",
  - "L2_GAS.max_price_per_unit * L2_GAS.max_amount,",
  - "tip * L2_GAS.max_amount, the tip described above."
```
  = 

```json
{
  "1": "MAX_ESCAPE_TIP_STRK = 1 STRK which limits the result of multiplying tip * L2_GAS.max_amount.",
  "2": "MAX_ESCAPE_MAX_FEE_STRK = 50 STRK which limits the sum of all of the following:",
  "2-1": "L1_GAS.max_price_per_unit * L1_GAS.max_amount,", 
  "2-2": "L2_GAS.max_price_per_unit * L2_GAS.max_amount,", 
  "2-3": "tip * L2_GAS.max_amount, the tip described above." 
}
```

