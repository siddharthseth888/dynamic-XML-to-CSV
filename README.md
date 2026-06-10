# Dynamic XML to CSV Flattener

## Overview
This Python utility automatically parses, flattens, and extracts data from deeply nested XML files into structured, analysis-ready CSV formats.

It handles hierarchical XML data dynamically—meaning it determines column sizing and ordering on the fly without needing hardcoded schemas. A JSON configuration file (`config.json`) dictates which specific root tags to extract, making this script highly reusable for various XML data structures (such as smart meter logs, utility billing data, or complex configuration files).

## Key Features
* **Dynamic Hierarchy Flattening:** Converts multi-level XML nodes and their attributes into a structured tabular (Long Format) layout.
* **Intelligent Column Sizing:** Automatically calculates the maximum depth and maximum number of attributes to build the CSV structure without breaking.
* **The "Ultimate Sweeper":** Automatically drops columns that evaluate to 100% blank to keep the final output clean and lean.
* **Configuration-Driven:** Uses a `config.json` file to selectively target and export only the necessary XML tags, preventing massive, cluttered outputs.

## Prerequisites
This script requires Python 3.x and the `pandas` library.

Install Pandas via pip:
```bash
pip install pandas
```

To play with the code:
```bash
git clone https://github.com/siddharthseth888/dynamic-XML-to-CSV
```
```bash
cd dynamic-XML-to-CSV
```
```bash
python3 main.py
```

If this doesn't work create a virtual environment by:
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```
```bash
python3 main.py
```


and after that give the file name of the XML file for eg in our case egSS31.cdf
```bash
egSS31.cdf
```

#### This will generate the separate CSV files for all the XML parent tags.
#### *NOTE->* CDF and XML are the same. You can upload any raw file for the same!
