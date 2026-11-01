# Task 2: Sales Data Analysis with Pandas

## Overview

This beginner-friendly project analyzes transaction-level retail sales data with Pandas. It checks data quality, calculates key sales metrics, compares categories and gender groups, and reviews monthly sales trends.

The dataset was downloaded from Kaggle: [Retail Sales Dataset — Mohammad Talib](https://www.kaggle.com/datasets/mohammadtalib786/retail-sales-dataset). Attribution is retained to the original dataset author and Kaggle source.

## Dataset

The analysis uses `data/raw/retail_sales.csv`, with 1,000 rows and these columns:

- `Transaction ID`
- `Date`
- `Customer ID`
- `Gender`
- `Age`
- `Product Category`
- `Quantity`
- `Price per Unit`
- `Total Amount`

## Libraries

- Python 3.13 (requested)
- Pandas
- Matplotlib
- Seaborn
- Jupyter Notebook

## Folder structure

```text
Task_2_Sales_Analysis/
├── data/
│   └── raw/
│       └── retail_sales.csv
├── notebooks/
│   └── sales_analysis.ipynb
├── reports/
│   └── sales_analysis_report.md
└── README.md
```

## Execution

From the `Task_2_Sales_Analysis/notebooks/` folder, run:

```bash
jupyter nbconvert --to notebook --execute sales_analysis.ipynb --output sales_analysis.ipynb
```

The executed notebook saves its tables and visualizations in the notebook file. The analysis uses the existing root project dependencies.

## Dataset Attribution

- **Dataset:** Retail Sales Dataset
- **Creator:** Mohammad Talib
- **Source:** [Kaggle – Retail Sales Dataset](https://www.kaggle.com/datasets/mohammadtalib786/retail-sales-dataset)
- **License:** [CC0 1.0 Universal (Public Domain Dedication)](https://creativecommons.org/publicdomain/zero/1.0/)

The dataset is made available under the CC0 1.0 licence, permitting reuse, modification, and redistribution.