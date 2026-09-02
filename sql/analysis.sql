WITH valid_orders AS (
    SELECT
        order_id,
        order_date,
        customer_id,
        product_id,
        category,
        region,
        acquisition_channel,
        quantity,
        discount_pct,
        returned,
        quantity * unit_price * (1 - discount_pct) * (1 - returned) AS net_revenue,
        quantity * unit_cost * (1 - returned) AS cost
    FROM transactions
)
SELECT
    strftime('%Y-%m', order_date) AS month,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT customer_id) AS active_customers,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(net_revenue - cost), 2) AS profit,
    ROUND(SUM(net_revenue) / COUNT(DISTINCT order_id), 2) AS average_order_value
FROM valid_orders
GROUP BY month
ORDER BY month;

SELECT
    category,
    ROUND(SUM(quantity * unit_price * (1 - discount_pct) * (1 - returned)), 2) AS net_revenue,
    ROUND(SUM((quantity * unit_price * (1 - discount_pct) - quantity * unit_cost) * (1 - returned)), 2) AS profit,
    ROUND(AVG(returned) * 100, 2) AS return_rate_pct
FROM transactions
GROUP BY category
ORDER BY profit DESC;

WITH customer_value AS (
    SELECT
        customer_id,
        region,
        acquisition_channel,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(quantity * unit_price * (1 - discount_pct) * (1 - returned)) AS lifetime_revenue
    FROM transactions
    GROUP BY customer_id, region, acquisition_channel
)
SELECT
    acquisition_channel,
    COUNT(*) AS customers,
    ROUND(AVG(order_count), 2) AS average_orders,
    ROUND(AVG(lifetime_revenue), 2) AS average_customer_value,
    ROUND(SUM(lifetime_revenue), 2) AS total_revenue
FROM customer_value
GROUP BY acquisition_channel
ORDER BY average_customer_value DESC;

SELECT
    product_id,
    category,
    SUM(quantity) AS units_sold,
    ROUND(SUM(quantity * unit_price * (1 - discount_pct) * (1 - returned)), 2) AS net_revenue,
    ROUND(SUM((quantity * unit_price * (1 - discount_pct) - quantity * unit_cost) * (1 - returned)), 2) AS profit
FROM transactions
GROUP BY product_id, category
ORDER BY profit DESC
LIMIT 10;

