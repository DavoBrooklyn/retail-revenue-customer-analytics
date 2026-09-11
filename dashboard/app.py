from pathlib import Path
import subprocess
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"
DATA = ROOT / "data" / "processed" / "clean_transactions.csv"

st.set_page_config(page_title="Retail Revenue & Customer Analytics", page_icon="📊", layout="wide")

if not DATA.exists() or not (OUTPUT / "monthly_summary.csv").exists():
    subprocess.run([sys.executable, str(ROOT / "run.py")], check=True, cwd=ROOT)

@st.cache_data
def load_data():
    transactions = pd.read_csv(DATA, parse_dates=["order_date"])
    monthly = pd.read_csv(OUTPUT / "monthly_summary.csv")
    segments = pd.read_csv(OUTPUT / "customer_segments.csv")
    retention = pd.read_csv(OUTPUT / "cohort_retention.csv", index_col=0)
    return transactions, monthly, segments, retention

transactions, monthly, segments, retention = load_data()

st.title("Retail Revenue & Customer Analytics")
st.caption("End-to-end portfolio project built with Python, pandas, SQL and Streamlit")

with st.sidebar:
    st.header("Filters")
    regions = st.multiselect("Region", sorted(transactions["region"].unique()), default=sorted(transactions["region"].unique()))
    categories = st.multiselect("Category", sorted(transactions["category"].unique()), default=sorted(transactions["category"].unique()))
    channels = st.multiselect("Acquisition Channel", sorted(transactions["acquisition_channel"].unique()), default=sorted(transactions["acquisition_channel"].unique()))

filtered = transactions[transactions["region"].isin(regions) & transactions["category"].isin(categories) & transactions["acquisition_channel"].isin(channels)].copy()

revenue = filtered["net_revenue"].sum()
profit = filtered["profit"].sum()
orders = filtered["order_id"].nunique()
margin = profit / revenue if revenue else 0
aov = revenue / orders if orders else 0
return_rate = filtered["returned"].mean() if len(filtered) else 0

tab1, tab2, tab3 = st.tabs(["Executive Overview", "Customer Analytics", "Product & Channel Analytics"])

with tab1:
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Net Revenue", f"${revenue/1_000_000:.2f}M")
    c2.metric("Gross Profit", f"${profit/1_000_000:.2f}M")
    c3.metric("Profit Margin", f"{margin:.1%}")
    c4.metric("Orders", f"{orders:,}")
    c5.metric("AOV", f"${aov:,.0f}")
    c6.metric("Return Rate", f"{return_rate:.1%}")

    monthly_filtered = filtered.groupby("month", as_index=False).agg(net_revenue=("net_revenue", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
    fig = px.line(monthly_filtered, x="month", y=["net_revenue", "profit"], markers=True, title="Revenue and Profit Trend")
    fig.update_layout(yaxis_title="USD", xaxis_title="Month", legend_title_text="Metric", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    region_summary = filtered.groupby("region", as_index=False).agg(net_revenue=("net_revenue", "sum"), profit=("profit", "sum"))
    left.plotly_chart(px.bar(region_summary.sort_values("net_revenue"), x="net_revenue", y="region", orientation="h", title="Revenue by Region"), use_container_width=True)
    payment = filtered.groupby("payment_method", as_index=False)["net_revenue"].sum()
    right.plotly_chart(px.pie(payment, values="net_revenue", names="payment_method", hole=.55, title="Revenue by Payment Method"), use_container_width=True)

with tab2:
    segment_summary = segments.groupby("segment", as_index=False).agg(customers=("customer_id", "count"), revenue=("monetary", "sum"), average_value=("monetary", "mean"))
    left, right = st.columns(2)
    left.plotly_chart(px.bar(segment_summary.sort_values("revenue"), x="revenue", y="segment", orientation="h", title="Revenue by RFM Segment"), use_container_width=True)
    right.plotly_chart(px.bar(segment_summary.sort_values("customers"), x="customers", y="segment", orientation="h", title="Customers by RFM Segment"), use_container_width=True)

    heat = retention.copy()
    heat.columns = [str(c) for c in heat.columns]
    fig = go.Figure(data=go.Heatmap(z=heat.values, x=heat.columns, y=heat.index, colorscale="Blues", zmin=0, zmax=1, hovertemplate="Cohort %{y}<br>Month %{x}<br>Retention %{z:.1%}<extra></extra>"))
    fig.update_layout(title="Customer Cohort Retention", xaxis_title="Months Since First Purchase", yaxis_title="Cohort Month", height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Customer Segments")
    st.dataframe(segment_summary.sort_values("revenue", ascending=False).style.format({"revenue": "${:,.0f}", "average_value": "${:,.0f}"}), use_container_width=True, hide_index=True)

with tab3:
    category_filtered = filtered.groupby("category", as_index=False).agg(net_revenue=("net_revenue", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
    category_filtered["profit_margin"] = category_filtered["profit"] / category_filtered["net_revenue"]
    channel_filtered = filtered[filtered["returned"] == 0].groupby("acquisition_channel", as_index=False).agg(customers=("customer_id", "nunique"), net_revenue=("net_revenue", "sum"), profit=("profit", "sum"))
    channel_filtered["revenue_per_customer"] = channel_filtered["net_revenue"] / channel_filtered["customers"]

    left, right = st.columns(2)
    left.plotly_chart(px.bar(category_filtered.sort_values("profit"), x="profit", y="category", orientation="h", title="Profit by Category"), use_container_width=True)
    right.plotly_chart(px.bar(category_filtered.sort_values("profit_margin"), x="profit_margin", y="category", orientation="h", title="Profit Margin by Category"), use_container_width=True)

    left, right = st.columns(2)
    left.plotly_chart(px.bar(channel_filtered.sort_values("revenue_per_customer"), x="revenue_per_customer", y="acquisition_channel", orientation="h", title="Revenue per Customer by Acquisition Channel"), use_container_width=True)
    right.plotly_chart(px.scatter(category_filtered, x="net_revenue", y="profit_margin", size="orders", text="category", title="Category Revenue vs Margin"), use_container_width=True)

    st.subheader("Business Takeaways")
    top_category = category_filtered.loc[category_filtered["profit"].idxmax(), "category"]
    best_margin = category_filtered.loc[category_filtered["profit_margin"].idxmax(), "category"]
    best_channel = channel_filtered.loc[channel_filtered["revenue_per_customer"].idxmax(), "acquisition_channel"]
    st.write(f"Highest total profit category: **{top_category}**")
    st.write(f"Strongest margin category: **{best_margin}**")
    st.write(f"Highest revenue per customer channel: **{best_channel}**")
