from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/transactions.csv"
PROCESSED = ROOT / "data/processed"
OUTPUT = ROOT / "outputs"

def load_data():
    df = pd.read_csv(RAW, parse_dates=["order_date"])
    df = df.drop_duplicates(subset="order_id")
    numeric = ["quantity","discount_pct","unit_price","unit_cost","returned"]
    df[numeric] = df[numeric].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=["customer_id","product_id","order_date"] + numeric)
    df = df[(df.quantity > 0) & (df.unit_price > 0) & (df.unit_cost >= 0)]
    df["gross_revenue"] = df.quantity * df.unit_price
    df["net_revenue"] = df.gross_revenue * (1-df.discount_pct) * (1-df.returned)
    df["cost"] = df.quantity * df.unit_cost * (1-df.returned)
    df["profit"] = df.net_revenue - df.cost
    df["month"] = df.order_date.dt.to_period("M").astype(str)
    return df

def create_monthly_summary(df):
    m = df.groupby("month", as_index=False).agg(orders=("order_id","nunique"),customers=("customer_id","nunique"),net_revenue=("net_revenue","sum"),profit=("profit","sum"),returns=("returned","sum"))
    m["aov"] = m.net_revenue / m.orders
    m["profit_margin"] = m.profit / m.net_revenue.replace(0,np.nan)
    m["revenue_growth"] = m.net_revenue.pct_change()
    return m

def create_rfm(df):
    snapshot = df.order_date.max() + pd.Timedelta(days=1)
    rfm = df[df.returned == 0].groupby("customer_id").agg(recency=("order_date",lambda x:(snapshot-x.max()).days),frequency=("order_id","nunique"),monetary=("net_revenue","sum"))
    rfm["r_score"] = pd.qcut(rfm.recency.rank(method="first"),5,labels=[5,4,3,2,1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm.frequency.rank(method="first"),5,labels=[1,2,3,4,5]).astype(int)
    rfm["m_score"] = pd.qcut(rfm.monetary.rank(method="first"),5,labels=[1,2,3,4,5]).astype(int)
    cond=[(rfm.r_score>=4)&(rfm.f_score>=4),(rfm.r_score>=3)&(rfm.f_score>=3),(rfm.r_score>=4)&(rfm.f_score<=2),(rfm.r_score<=2)&(rfm.f_score>=4),(rfm.r_score<=2)&(rfm.f_score<=2)]
    rfm["segment"] = np.select(cond,["Champions","Loyal","Promising","At Risk","Hibernating"],default="Regular")
    return rfm.reset_index()

def create_cohort_retention(df):
    o=df[df.returned==0].copy(); o["order_month"]=o.order_date.dt.to_period("M")
    o["cohort_month"]=o.groupby("customer_id")["order_month"].transform("min")
    o["cohort_index"]=(o.order_month.dt.year-o.cohort_month.dt.year)*12+o.order_month.dt.month-o.cohort_month.dt.month
    c=o.groupby(["cohort_month","cohort_index"])["customer_id"].nunique().unstack(fill_value=0)
    r=c.divide(c[0],axis=0); r.index=r.index.astype(str); return r

def save_outputs(df,m,rfm,r):
    PROCESSED.mkdir(parents=True,exist_ok=True); OUTPUT.mkdir(parents=True,exist_ok=True)
    category=df.groupby("category",as_index=False).agg(orders=("order_id","nunique"),net_revenue=("net_revenue","sum"),profit=("profit","sum"),returns=("returned","sum"))
    category["profit_margin"]=category.profit/category.net_revenue.replace(0,np.nan)
    channel=df[df.returned==0].groupby("acquisition_channel",as_index=False).agg(customers=("customer_id","nunique"),orders=("order_id","nunique"),net_revenue=("net_revenue","sum"),profit=("profit","sum"))
    channel["revenue_per_customer"]=channel.net_revenue/channel.customers
    kpis=pd.DataFrame([{"net_revenue":df.net_revenue.sum(),"gross_profit":df.profit.sum(),"profit_margin":df.profit.sum()/df.net_revenue.sum(),"orders":df.order_id.nunique(),"aov":df.net_revenue.sum()/df.order_id.nunique(),"customers":df.customer_id.nunique(),"return_rate":df.returned.mean()}])
    df.to_csv(PROCESSED/"clean_transactions.csv",index=False); m.to_csv(OUTPUT/"monthly_summary.csv",index=False); rfm.to_csv(OUTPUT/"customer_segments.csv",index=False); r.to_csv(OUTPUT/"cohort_retention.csv"); category.to_csv(OUTPUT/"category_summary.csv",index=False); channel.to_csv(OUTPUT/"channel_summary.csv",index=False); kpis.to_csv(OUTPUT/"executive_kpis.csv",index=False)
    fig,ax=plt.subplots(figsize=(10,5)); ax.plot(m.month,m.net_revenue,marker="o"); ax.set_title("Monthly Net Revenue"); ax.tick_params(axis="x",rotation=45); fig.tight_layout(); fig.savefig(OUTPUT/"monthly_revenue.png",dpi=150); plt.close(fig)

def main():
    df=load_data(); m=create_monthly_summary(df); rfm=create_rfm(df); r=create_cohort_retention(df); save_outputs(df,m,rfm,r)
    k=pd.read_csv(OUTPUT/"executive_kpis.csv").iloc[0]
    print(f"Revenue ${k.net_revenue:,.0f} | Profit ${k.gross_profit:,.0f} | Margin {k.profit_margin:.1%} | Orders {int(k.orders):,} | AOV ${k.aov:,.0f}")

if __name__ == "__main__": main()
