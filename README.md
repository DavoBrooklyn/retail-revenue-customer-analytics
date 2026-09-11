# Retail Revenue & Customer Analytics

An end-to-end business intelligence portfolio project that turns raw retail transactions into commercial insights for revenue, profitability, retention, customer value, products, and acquisition channels.

## Business Problem

Retail teams often have transaction data but no single view of what is driving revenue, profit, customer retention, and channel quality. This project builds a reproducible analytics pipeline and interactive dashboard to answer those questions.

The project is designed around decisions a BI analyst would support:

- Is revenue growing and is that growth profitable?
- Which product categories generate the most profit?
- Which customers are the most valuable and which are at risk?
- How well do customer cohorts retain after acquisition?
- Which acquisition channels bring higher-value customers?
- Where should retention, marketing, and merchandising attention be focused?

## End-to-End Flow

`Synthetic transactions -> Python/pandas cleaning -> KPI calculations -> RFM segmentation -> cohort retention -> SQL analysis -> dashboard-ready outputs -> Streamlit dashboard`

## Tech Stack

- Python
- pandas
- NumPy
- SQL
- Plotly
- Streamlit
- Matplotlib

## Dashboard

The interactive dashboard has three sections.

### Executive Overview

- Net revenue
- Gross profit
- Profit margin
- Orders
- Average order value
- Return rate
- Revenue and profit trend
- Revenue by region
- Payment-method mix

### Customer Analytics

- RFM customer segmentation
- Revenue by segment
- Customer count by segment
- Cohort retention heatmap

### Product & Channel Analytics

- Profit by category
- Margin by category
- Revenue per customer by acquisition channel
- Category revenue vs margin
- Dynamic business takeaways

Filters allow the dashboard to be explored by region, category, and acquisition channel.

## Reproducible Project Results

With the default random seed, the project produces approximately:

- Net revenue: $2.87M
- Gross profit: $1.22M
- Profit margin: 42.4%
- Orders: 10,083
- Average order value: $285
- Customers: 945
- Return rate: 7.1%

In this generated dataset, Electronics produces the highest total category profit and Social has the highest revenue per customer among acquisition channels.

## Project Structure

```text
retail-revenue-customer-analytics/
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   └── VIDEO_WALKTHROUGH.md
├── outputs/
├── sql/
│   └── analysis.sql
├── src/
│   ├── analyze.py
│   └── generate_data.py
├── run.py
├── start_dashboard.bat
└── requirements.txt
```

## Run the Project

### Windows

Double-click `start_dashboard.bat`, or run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

The dashboard automatically generates the dataset and analysis outputs if they do not exist yet.

### macOS or Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

## Generated Outputs

- `data/processed/clean_transactions.csv`
- `outputs/executive_kpis.csv`
- `outputs/monthly_summary.csv`
- `outputs/customer_segments.csv`
- `outputs/cohort_retention.csv`
- `outputs/category_summary.csv`
- `outputs/channel_summary.csv`

## Methodology

Net revenue is calculated after discounts and returns. Gross profit subtracts product cost from net revenue. RFM scoring ranks customers on recency, frequency, and monetary value and maps them into business-friendly segments. Cohort analysis groups customers by their first purchase month and tracks repeat activity over time.

## Portfolio Note

The dataset is reproducibly generated synthetic data. It is intentionally non-confidential and is used to demonstrate the same workflow, analytical reasoning, and decision-support approach that would be used on real business data. The project does not claim measured impact at a real company.
