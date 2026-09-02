from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "transactions.csv"
PROCESSED = ROOT / "data" / "processed"
OUTPUT = ROOT / "outputs"


def load_data():
    df = pd.read_csv(RAW, parse_dates=["order_date"])
    df = df.drop_duplicates(subset="order_id")
    numeric = ["quantity", "discount_pct", "unit_price", "unit_cost", "returned"]
    df[numeric] = df[numeric].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=["customer_id", "product_id", "order_date"] + numeric)
    df = df[(df["quantity"] > 0) & (df["unit_price"] > 0) & (df["unit_cost"] >= 0)]
    df["gross_revenue"] = df["quantity"] * df["unit_price"]
    df["net_revenue"] = df["gross_revenue"] * (1 - df["discount_pct"]) * (1 - df["returned"])
    df["cost"] = df["quantity"] * df["unit_cost"] * (1 - df["returned"])
    df["profit"] = df["net_revenue"] - df["cost"]
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df


def create_monthly_summary(df):
    monthly = df.groupby("month", as_index=False).agg(
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique"),
        net_revenue=("net_revenue", "sum"),
        profit=("profit", "sum"),
        returns=("returned", "sum")
    )
    monthly["aov"] = monthly["net_revenue"] / monthly["orders"]
    monthly["profit_margin"] = monthly["profit"] / monthly["net_revenue"]
    monthly["revenue_growth"] = monthly["net_revenue"].pct_change()
    return monthly


def create_rfm(df):
    snapshot = df["order_date"].max() + pd.Timedelta(days=1)
    rfm = df[df["returned"] == 0].groupby("customer_id").agg(
        recency=("order_date", lambda x: (snapshot - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("net_revenue", "sum")
    )
    rfm["r_score"] = pd.qcut(rfm["recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    conditions = [
        (rfm["r_score"] >= 4) & (rfm["f_score"] >= 4),
        (rfm["r_score"] >= 3) & (rfm["f_score"] >= 3),
        (rfm["r_score"] >= 4) & (rfm["f_score"] <= 2),
        (rfm["r_score"] <= 2) & (rfm["f_score"] >= 4),
        (rfm["r_score"] <= 2) & (rfm["f_score"] <= 2)
    ]
    labels = ["Champions", "Loyal", "Promising", "At Risk", "Hibernating"]
    rfm["segment"] = np.select(conditions, labels, default="Regular")
    return rfm.reset_index()


def create_cohort_retention(df):
    orders = df[df["returned"] == 0].copy()
    orders["order_month"] = orders["order_date"].dt.to_period("M")
    orders["cohort_month"] = orders.groupby("customer_id")["order_month"].transform("min")
    orders["cohort_index"] = (orders["order_month"].dt.year - orders["cohort_month"].dt.year) * 12 + orders["order_month"].dt.month - orders["cohort_month"].dt.month
    cohort = orders.groupby(["cohort_month", "cohort_index"])["customer_id"].nunique().unstack(fill_value=0)
    retention = cohort.divide(cohort[0], axis=0)
    retention.index = retention.index.astype(str)
    return retention


def save_charts(monthly, rfm, retention, df):
    sns.set_theme(style="whitegrid", palette="deep")
    OUTPUT.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly, x="month", y="net_revenue", marker="o", ax=ax)
    ax.set(title="Monthly Net Revenue", xlabel="Month", ylabel="Net Revenue ($)")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(OUTPUT / "monthly_revenue.png", dpi=160)
    plt.close(fig)

    segment = rfm.groupby("segment", as_index=False).agg(customers=("customer_id", "count"), revenue=("monetary", "sum")).sort_values("revenue", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=segment, x="revenue", y="segment", ax=ax)
    ax.set(title="Revenue by Customer Segment", xlabel="Revenue ($)", ylabel="Segment")
    fig.tight_layout()
    fig.savefig(OUTPUT / "rfm_segments.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.heatmap(retention.iloc[-12:, :12], cmap="Blues", fmt=".0%", annot=True, ax=ax)
    ax.set(title="Customer Cohort Retention", xlabel="Months Since First Purchase", ylabel="Cohort")
    fig.tight_layout()
    fig.savefig(OUTPUT / "cohort_retention.png", dpi=160)
    plt.close(fig)

    category = df.groupby("category", as_index=False).agg(net_revenue=("net_revenue", "sum"), profit=("profit", "sum"))
    category["profit_margin"] = category["profit"] / category["net_revenue"]
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=category.sort_values("profit_margin", ascending=False), x="profit_margin", y="category", ax=ax)
    ax.set(title="Profit Margin by Category", xlabel="Profit Margin", ylabel="Category")
    ax.xaxis.set_major_formatter(lambda x, pos: f"{x:.0%}")
    fig.tight_layout()
    fig.savefig(OUTPUT / "category_margin.png", dpi=160)
    plt.close(fig)


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    df = load_data()
    monthly = create_monthly_summary(df)
    rfm = create_rfm(df)
    retention = create_cohort_retention(df)
    df.to_csv(PROCESSED / "clean_transactions.csv", index=False)
    monthly.to_csv(OUTPUT / "monthly_summary.csv", index=False)
    rfm.to_csv(OUTPUT / "customer_segments.csv", index=False)
    retention.to_csv(OUTPUT / "cohort_retention.csv")
    save_charts(monthly, rfm, retention, df)


if __name__ == "__main__":
    main()
