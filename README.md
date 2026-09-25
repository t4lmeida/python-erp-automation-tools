# ⚙️ Enterprise ERP & Infrastructure Automation Tools

## 📌 Executive Summary
This repository is a collection of Python and SQL-based automation tools, ETL scripts, and internal GUI applications developed to bypass legacy ERP limitations, optimize data extraction, and empower operational teams with self-service capabilities. 

The primary business objective across these modules is to reduce manual administrative hours, eliminate human error in the billing/shipping pipeline, and provide actionable data for management decision-making.

## 🛠️ Tech Stack & Concepts Applied
- **Languages & Scripting:** Python 3, SQL (Views, Joins)
- **Architecture & Design:** Monorepo structure, Internal Tooling, GUI Wrappers
- **Integrations:** REST APIs, Windows Task Scheduler Automation, Docker
- **Data Engineering:** HTML Parsing, ETL Pipelines, Regular Expressions (RegEx)

## 📁 Repository Structure & Modules

| Module | Description | Business Impact |
| **`zpl-label-preview-tool/`** | Python desktop application integrating with REST APIs to render and edit ZPL (Zebra) labels. | Eliminated IT support dependency for shipping label adjustments; reduced printing errors. |
| **`erp-financial-extractors/`** | Data extraction scripts converting raw HTML/System data into structured formats. | Automated payroll and financial reporting, reducing manual closing time. |
| **`voip-click2call/`** | API integration script for Yealink IP phones. | Enabled 1-click calling directly from PC, optimizing operational efficiency. |

---
*Developed by **Thiago Oliveira Almeida** - IT & Infrastructure Analyst | Data Science Student*
