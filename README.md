# Quantitative Developer Assignment

This project downloads historical stock data from Yahoo Finance, performs basic financial analysis, and generates a PDF report with visualizations and strategy evaluation.

For a detailed explanation of the analysis and methodology, refer to the exploratory notebook:

`notebooks/exploratory_analysis.ipynb`

---

# Requirements

Python 3.x

Install required libraries:

```
pip install pandas numpy yfinance matplotlib seaborn
```

---

# How to Run the Script

Run the main script:

```
python quant_analysis.py
```

You will be prompted to enter:

```
Time unit (days / months / years)
Time value
Data interval (1m, 5m, 1h, 1d, 1wk, 1mo, etc.)
Stock tickers separated by space
```

Example:

```
years
3
1d
AAPL MSFT NVDA
```

---

# Output

The script automatically creates the following folders if they do not exist:

```
data/
reports/
```

### Raw Data

Downloaded data is saved to:

```
data/raw_data_TIMESTAMP.csv
```

### Analysis Report

A PDF report containing charts and strategy results is saved to:

```
reports/quant_report_TIMESTAMP.pdf
```

---

# Additional Notes

The notebook `notebooks/exploratory_analysis.ipynb` contains the exploratory analysis and detailed explanations of the methods used in the script.
