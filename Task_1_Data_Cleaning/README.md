# Task 1: Data Cleaning — Cafe Sales Dataset

**Internship Project:** `Internship_Data_Analytics`  
**Task:** Task 1 — Data Cleaning & Quality Assessment  
**Author:** Antigravity AI Coding Assistant  
**Date:** November 2026  

---

## 1. Project Overview

This project implements an end-to-end data cleaning, quality assurance, and numerical recovery pipeline for retail sales records from a cafe enterprise. The raw data exhibits common real-world data corruption patterns, including textual error sentinels (`ERROR`, `UNKNOWN`), missing values across financial and categorical attributes, and data type mismatches.

The objective of Task 1 is to diagnose data quality anomalies, standardize corruptions using null-safe procedures, enforce native physical types, perform mathematically governed numerical recovery ($\text{Quantity} \times \text{Price} = \text{Total}$), and track data provenance without fabricating categorical values or deleting observations.

---

## 2. Dataset Source & Licensing Disclosure

* **Dataset Name:** Cafe Sales — Dirty Data for Cleaning Training
* **Author / Uploader:** Ahmed Mohamed (`ahmedmohamed2003`)
* **Canonical Source:** [Kaggle Dataset: Cafe Sales - Dirty Data for Cleaning Training](https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training)
* **Dataset License:** **Unspecified / Unknown**

### Important Licensing & Redistribution Notice:
> **No Dataset Redistribution:**  
> Because the dataset license on Kaggle is unspecified/unknown, the original author retains all default copyright protections. In compliance with copyright and intellectual property standards, **this public repository does not redistribute or bundle the raw dataset (`archive.zip`, `dirty_cafe_sales.csv`) or the derivative cleaned dataset (`cleaned_cafe_sales.csv`)**.  
>  
> All data files are excluded via `.gitignore`. Users must download the raw dataset directly from Kaggle and generate the cleaned dataset locally using the provided pipeline script.

---

## 3. Local Dataset Setup & Directory Structure

To run the cleaning pipeline or execute the notebook locally, follow these steps to place the data in the expected directory structure:

### Step-by-Step Setup:
1. Navigate to the [Kaggle Dataset Page](https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training) and sign in.
2. Click **Download** to obtain the `archive.zip` file.
3. Save the downloaded archive to:
   ```text
   Task_1_Data_Cleaning/data/raw/archive.zip
   ```
4. Extract `dirty_cafe_sales.csv` from the zip file into:
   ```text
   Task_1_Data_Cleaning/data/raw/extracted/dirty_cafe_sales.csv
   ```

### Project Folder Hierarchy:
```text
Task_1_Data_Cleaning/
├── README.md                                # Project documentation and user guide
├── data/
│   ├── cleaned/
│   │   ├── .gitkeep                         # Tracked directory placeholder
│   │   └── cleaned_cafe_sales.csv           # Generated LOCALLY via pipeline (Git-ignored)
│   └── raw/
│       ├── .gitkeep                         # Tracked directory placeholder
│       ├── archive.zip                      # Downloaded LOCALLY from Kaggle (Git-ignored)
│       └── extracted/
│           ├── .gitkeep                     # Tracked directory placeholder
│           └── dirty_cafe_sales.csv         # Extracted LOCALLY from archive (Git-ignored)
├── notebooks/
│   └── data_cleaning.ipynb                  # Interactive inspection, cleaning & audit notebook
├── reports/
│   └── cleaning_report.md                   # Formal data cleaning and audit report
└── src/
    └── cleaning.py                          # Automated, modular Python cleaning script
```

---

## 4. Dataset Schema

When downloaded, the dataset contains 10,000 transactions with the following attributes:
* `Transaction ID`: Unique alphanumeric identifier (`TXN_xxxxxxx`)
* `Item`: Food or beverage product (8 menu items: Cake, Coffee, Cookie, Juice, Salad, Sandwich, Smoothie, Tea)
* `Quantity`: Number of units purchased ($1 \le Q \le 5$)
* `Price Per Unit`: Constant fixed price per unit in USD ($1.0 to $5.0)
* `Total Spent`: Gross transaction expenditure in USD
* `Payment Method`: Payment channel (`Cash`, `Credit Card`, `Digital Wallet`)
* `Location`: Transaction venue (`In-store`, `Takeaway`)
* `Transaction Date`: Date of sale in ISO 8601 (`YYYY-MM-DD`)

When cleaned locally by `src/cleaning.py`, three boolean audit columns are attached to track data lineage:
* `is_quantity_imputed`: `True` if quantity was mathematically recovered; `False` if observed.
* `is_price_imputed`: `True` if price was mathematically recovered; `False` if observed.
* `is_total_imputed`: `True` if total was mathematically recovered; `False` if observed.

---

## 5. Installation & Environment Setup

This project requires **Python 3.10+** (Python 3.13 recommended) with the following scientific packages:

```powershell
# Install core dependencies
py -3.13 -m pip install pandas numpy matplotlib seaborn ipykernel nbformat nbclient

# Register the Python 3.13 Jupyter kernel (optional for notebook execution)
py -3.13 -m ipykernel install --user --name python313 --display-name "Python 3.13"
```

---

## 6. How to Run the Cleaning Pipeline

Once the raw dataset has been placed in `Task_1_Data_Cleaning/data/raw/extracted/dirty_cafe_sales.csv`, run the pipeline from the repository root:

```powershell
# Navigate to repository root
cd "Internship_Data_Analytics"

# Run the automated cleaning script
py -3.13 Task_1_Data_Cleaning/src/cleaning.py
```

### Pipeline Workflow:
1. Loads raw CSV data in read-only mode (preserving raw SHA-256 integrity).
2. Standardizes text errors (`ERROR`, `UNKNOWN`, `NAN`, `NONE`, `NULL`, `NA`, `?`, whitespace) into `np.nan` using null-safe masking.
3. Converts physical data types (`Int64`, `float64`, `datetime64[ns]`).
4. Executes single-triad numerical recovery ($\text{Qty} \times \text{Price} = \text{Total}$).
5. Adds granular boolean provenance flags (`is_quantity_imputed`, `is_price_imputed`, `is_total_imputed`).
6. Executes automated validation suite:
   * Transaction ID uniqueness (100% unique)
   * Quantity domain integrity ($Q \in [1, 5]$)
   * Price domain integrity ($\{1.0, 1.5, 2.0, 3.0, 4.0, 5.0\}$)
   * Item category domain integrity (8 menu items)
   * Payment Method domain integrity (`Cash`, `Credit Card`, `Digital Wallet`)
   * Location domain integrity (`Takeaway`, `In-store`)
   * Item-Price alignment (0 contradictions)
   * Mathematical determinism (0 discrepancies)
   * Date parsing and explicit reporting of remaining missing timestamps
7. Exports cleaned CSV locally to `Task_1_Data_Cleaning/data/cleaned/cleaned_cafe_sales.csv` (excluded from Git).
8. Prints an audit table summarizing before-and-after metrics with dynamically calculated percentages.

---

## 7. How to Open the Jupyter Notebook

The interactive notebook contains the diagnostic inspection, data quality visualizations, live execution of the cleaning pipeline, and audit verification.

### Option A: In VS Code / Antigravity IDE
* Open the notebook directly: [`Task_1_Data_Cleaning/notebooks/data_cleaning.ipynb`](notebooks/data_cleaning.ipynb)
* Select the **Python 3.13** kernel in the top-right corner.
* Click **"Run All"** to execute all cells.

### Option B: In JupyterLab / Jupyter Notebook
```powershell
cd "Task_1_Data_Cleaning/notebooks"
py -3.13 -m jupyter lab
```

---

## 8. Artifact Directory & Git Status

| Artifact | Local Path | Included in Git? | Description |
| :--- | :--- | :---: | :--- |
| **Pipeline Script** | `Task_1_Data_Cleaning/src/cleaning.py` | **Yes** | Fully commented, modular Python cleaning script |
| **Audit Report** | `Task_1_Data_Cleaning/reports/cleaning_report.md` | **Yes** | Comprehensive audit findings and methodology documentation |
| **Interactive Notebook**| `Task_1_Data_Cleaning/notebooks/data_cleaning.ipynb`| **Yes** | Executed notebook with diagnostic plots (individual rows redacted) |
| **Project User Guide** | `Task_1_Data_Cleaning/README.md` | **Yes** | Setup, execution, licensing, and workflow documentation |
| **Raw Archive** | `Task_1_Data_Cleaning/data/raw/archive.zip` | **No (Git-ignored)** | Downloaded locally from Kaggle by user |
| **Raw CSV** | `Task_1_Data_Cleaning/data/raw/extracted/dirty_cafe_sales.csv` | **No (Git-ignored)** | Extracted locally from archive by user |
| **Cleaned CSV** | `Task_1_Data_Cleaning/data/cleaned/cleaned_cafe_sales.csv` | **No (Git-ignored)** | Generated locally upon running `cleaning.py` |
