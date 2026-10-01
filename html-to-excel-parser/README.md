# ⚙️ Auto Payroll: HTML to Excel ETL Pipeline

## 🎯 Business Problem
Financial and HR departments often face massive bottlenecks due to a lack of native integration between third-party accounting systems and corporate ERPs. In this scenario, the payroll data was exclusively provided as an unstructured, coordinate-based HTML report. This limitation forced the financial team to manually input hundreds of financial entries (credits and debits) into the ERP, a time-consuming process highly susceptible to human error.

## 💡 Technical Solution
Developed a local Extract, Transform, Load (ETL) pipeline to bypass system limitations and automate data entry. 
1. **Extract:** Parses the HTML DOM using `BeautifulSoup` and `Regex`, mapping X/Y CSS coordinates to identify employee IDs, names, transaction codes, and values.
2. **Transform:** Sanitizes extracted text, converts string formats to numeric values (`float`), and classifies transactions into Proventos (Credits) or Descontos (Debits).
3. **Load:** Exports the clean, structured dataset into an Excel matrix using `Openpyxl`, ready for immediate ERP ingestion or financial auditing.

To ensure scalability and autonomy for non-technical users, the pipeline is wrapped in a native Graphical User Interface (GUI) built with `Tkinter`.

## 🚀 Business Impact
* **100% Automation:** Eliminated manual data entry for payroll financial records.
* **Risk Mitigation:** Eradicated human errors in sensitive financial data transcription.
* **Operational Efficiency:** Empowered business users to execute the extraction in seconds without IT support intervention.

## 🛠️ Tech Stack
* **Python 3.x**
* **BeautifulSoup4** (HTML Parsing / Web Scraping)
* **Openpyxl** (Excel Report Generation)
* **Regex (`re`)** (Data Cleansing)
* **Tkinter** (Local GUI)

## ⚙️ How to Run

1. Clone this repository:
   ```bash
   git clone [https://github.com/t4lmeida/python-erp-automation-tools.git](https://github.com/t4lmeida/python-erp-automation-tools.git)```

2. Navigate to the project directory:
  ```bash
  cd python-erp-automation-tools/html-to-excel-parser```

3. Install dependencies:
  ```bash
  pip install -r requirements.txt```

4. Execute the application:
  ```bash
  python src/auto-payroll.py```
