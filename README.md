# Audit Report Crawlers

> This repository accompanies the paper **“SCAR: Mining and Structuring Smart Contract”**, submitted to the **ACM FSE 2026 Tool Demonstrations Track**.

**Authors (for citation):**  
Ilham Qasse<sup>*</sup>, Po‑Yu Tseng<sup>†</sup>, Mohammad Hamdaqa<sup>‡</sup>, and Gísli Hjálmtýsson<sup>*</sup>  

<sup>*</sup> Department of Computer Science, Reykjavik University, Reykjavik, Iceland  
<sup>†</sup> Department of Computer Science and Information Engineering, National Taiwan University, Taipei, Taiwan  
<sup>‡</sup> Department of Computer and Software Engineering, Polytechnique Montréal, Montréal, Canada  

Contact: `{ilham20,gisli}@ru.is`, `tsengben01@gmail.com`, `mhamdaqa@polymtl.ca`

## Description
- We collect audit reports from 4 companies or platfroms, which are **Code4rena**, **Consensys**, **Openzeppelin**, **Quantstamp**. 
- This project can currently be divided up into 2 parts: **Crawlers**, **Anaylers**. 
  - Crawlers: collect data from the 4 companies. 
  - Anaylers: classify and analyz the data collected by crawlers.
- For more details, please check out:
  - [crawler.md](crawler.md)
  - [analysis.md](analysis.md)

## Execution
Because of data dependencies, the correct order for execution is:
1. project crawlers
2. report crawlers
3. repo crawlers
4. analyzers
5. statistics

#### Run all at one time:
```shellscript=
$ python main.py
```

#### Using docker on Linux platform:
```shellscript=
$ cd audit-report-crawler
$ docker-compose up --build

# Enter interactive mode
$ docker-compose run audit-report-crawler /bin/bash

# Run main.py
$ docker-compose run audit-report-crawler python main.py
```

## Folder structure
### Modules
- crawlers
  - Crawlers for 4 companies. Each inherits base crawler. 
- analyzers
  - Analyzers for 4 companies. Each inherits base analyzer. 
- configs
  - Configs for 4 companies. Types, constants, dataclasses are defined here.
  - For example: **paths**, **urls**, **SeverityCount**, and so on.
- helpers
  - Functions related to crawlers and analyzers but supposed not to be methods will be defined under this folders.


