# 🏷️ ZPL Label Preview & Quantity Editor Tool

## 📐 The Business Challenge
In daily industrial labeling operations, adjusting print quantities on legacy `.zpl` (Zebra Programming Language) files requires operators to edit raw code. This often leads to formatting errors during dispatch and billing, generating constant low-level support tickets for the IT department.

## 💡 The Solution (Internal Tooling)
I orchestrated and designed a Python-based GUI application that acts as a bridge between the raw ZPL code and the non-technical production staff. 

By integrating with a ZPL rendering REST API (Labelary), the tool provides a real-time visual preview of the thermal label. It uses Regular Expressions (RegEx) to safely parse and inject the desired print quantity (`^PQ`) without the user ever seeing a line of code, saving the output as a fresh file to prevent data loss.

## 🚀 Impact & Key Results
- **Self-Service Automation:** Empowered the labeling team to handle 100% of label quantity adjustments independently.
- **Zero IT Overhead:** Eliminated Help Desk tickets related to ZPL syntax errors.
- **Risk Mitigation:** Real-time visual validation prevents costly mislabeling and material waste during high-volume shipping.

## 📚Libraries:
- requests
- re
-threading
-tkinter
-PIL (pillow)
-io (bytesIO)
