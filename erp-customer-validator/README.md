# ERP Customer Data Validator 🚀

## Overview
An automated data engineering pipeline designed to audit and validate enterprise customer records (ERP) against brazilian official government and postal databases. 

## 🎯 The Business Problem
During a database migration from a legacy system to a new ERP, thousands of customer records were imported without proper validation. Over time, this created a critical financial bottleneck: **banks and notary offices were rejecting the legal protest of unpaid invoices (duplicatas) due to invalid or mismatched customer addresses.** 

Instead of manually verifying thousands of records to fix the billing and shipping data, I developed this Python-based automated solution to cross-reference our internal database with official government APIs, instantly identifying which records needed maintenance to unlock the revenue recovery process.

## Key Features
*   **Secure Database Extraction**: Connects directly to the ERP database using environment variables (`.env`), ensuring no sensitive credentials are hardcoded.
*   **REST API Integration**: Consumes the [BrasilAPI](https://brasilapi.com.br/) to validate corporate names and full addresses.
*   **Smart Caching & Rate Limiting**: Implements an in-memory cache dictionary to avoid redundant API calls for recurring postal codes, saving processing time and preventing server overload. Includes dynamic delays to respect API rate limits.
*   **Data Normalization**: Cleanses and normalizes strings (removes accents, normalizes cases, removes trailing decimals from numeric IDs) to prevent false-positive mismatches between the ERP and the API.
*   **Automated Auditing**: Outputs a clean Excel (`.xlsx`) report pinpointing exactly which fields (Street, Neighborhood, City, Corporate Name) diverge from official government records.

## Tech Stack
*   **Language**: Python 3
*   **Data Manipulation**: `pandas`
*   **Web Requests**: `requests` (REST APIs)
*   **Security & Env**: `python-dotenv`
*   **Database**: SQL / `psycopg2` (PostgreSQL)

## Getting Started

### Prerequisites
Make sure you have Python installed. Clone this repository and install the required dependencies:

```bash
git clone [https://github.com/t4lmeida/python-erp-automation-tools/erp-customer-validator.git](https://github.com/t4lmeida/python-erp-automation-tools/erp-customer-validator.git)
cd erp-customer-validator
pip install -r requirements.txt```

*  Rename the .env.example file to .env
*  Fill in your local or testing database credentials inside the .env file:
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=yourpassword
DB_NAME=erp_database

### Execution
*  Run the main script to start the extraction and validation process:
python validador_cadastral.py


The script will display a real-time progress monitor in the terminal and, upon completion, generate an Auditoria_Cadastral.xlsx file containing the validation results.

###Security Note:
This repository includes a .gitignore file that prevents .env files and .xlsx data exports from being committed. Never upload real customer data or database passwords to GitHub.
