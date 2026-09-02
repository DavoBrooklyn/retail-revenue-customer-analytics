from pathlib import Path
import numpy as np
import pandas as pd


def main():
    rng = np.random.default_rng(42)
    output = Path(__file__).resolve().parents[1] / "data" / "raw"
    output.mkdir(parents=True, exist_ok=True)

    products = pd.DataFrame({
        "product_id": [f"P{i:03d}" for i in range(1, 41)],
        "category": np.repeat(["Electronics", "Home", "Beauty", "Sports", "Apparel"], 8),
        "unit_cost": np.round(rng.uniform(6, 180, 40), 2)
    })
    products["unit_price"] = np.round(products["unit_cost"] * rng.uniform(1.35, 2.2, 40), 2)

    customers = pd.DataFrame({
        "customer_id": [f"C{i:04d}" for i in range(1, 1001)],
        "region": rng.choice(["Yerevan", "Kotayk", "Shirak", "Lori", "Ararat"], 1000, p=[0.5, 0.16, 0.12, 0.11, 0.11]),
        "acquisition_channel": rng.choice(["Organic", "Paid Search", "Social", "Referral", "Email"], 1000, p=[0.28, 0.22, 0.2, 0.16, 0.14]),
        "signup_date": pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0, 650, 1000), unit="D")
    })

    n = 18000
    order_dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0, 730, n), unit="D")
    product_ids = rng.choice(products["product_id"], n)
    product_lookup = products.set_index("product_id")
    quantities = rng.choice([1, 2, 3, 4, 5], n, p=[0.54, 0.25, 0.12, 0.06, 0.03])
    discounts = rng.choice([0, 0.05, 0.1, 0.15, 0.2], n, p=[0.5, 0.16, 0.17, 0.1, 0.07])
    customer_weights = rng.pareto(2.5, 1000) + 0.15
    customer_weights /= customer_weights.sum()

    transactions = pd.DataFrame({
        "order_id": [f"O{i:06d}" for i in range(1, n + 1)],
        "order_date": order_dates,
        "customer_id": rng.choice(customers["customer_id"], n, p=customer_weights),
        "product_id": product_ids,
        "quantity": quantities,
        "discount_pct": discounts,
        "payment_method": rng.choice(["Card", "Cash", "Digital Wallet"], n, p=[0.52, 0.28, 0.2]),
        "returned": rng.choice([0, 1], n, p=[0.93, 0.07])
    })
    transactions["unit_price"] = transactions["product_id"].map(product_lookup["unit_price"])
    transactions["unit_cost"] = transactions["product_id"].map(product_lookup["unit_cost"])
    seasonal_factor = 1 + 0.18 * transactions["order_date"].dt.month.isin([11, 12])
    transactions["unit_price"] = np.round(transactions["unit_price"] * seasonal_factor, 2)
    transactions = transactions.merge(customers, on="customer_id", how="left")
    transactions = transactions[transactions["order_date"] >= transactions["signup_date"]].drop(columns="signup_date")
    transactions = transactions.merge(products[["product_id", "category"]], on="product_id", how="left")
    transactions.to_csv(output / "transactions.csv", index=False)


if __name__ == "__main__":
    main()

