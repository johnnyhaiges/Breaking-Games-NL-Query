
EXAMPLES = [
    {
        "question": "What are the top 5 products by total revenue?",
        "sql": (
            "SELECT product_title, SUM(revenue) AS total_revenue "
            "FROM shopify_sales "
            "GROUP BY product_title "
            "ORDER BY total_revenue DESC "
            "LIMIT 5;"
        ),
    },
    {
        "question": "How many checkouts reached the payment step versus how many did not?",
        "sql": (
            "SELECT "
            "  SUM(CASE WHEN payment_method IS NOT NULL THEN 1 ELSE 0 END) AS reached_payment, "
            "  SUM(CASE WHEN payment_method IS NULL THEN 1 ELSE 0 END) AS did_not_reach_payment "
            "FROM shopify_checkouts;"
        ),
    },
    {
        "question": "Which Meta campaign had the highest total spend?",
        "sql": (
            "SELECT campaign_name, SUM(spend) AS total_spend "
            "FROM meta_campaigns "
            "GROUP BY campaign_name "
            "ORDER BY total_spend DESC "
            "LIMIT 1;"
        ),
    },
    {
        "question": "How many distinct products are in the catalog?",
        "sql": "SELECT COUNT(DISTINCT product_title) AS product_count FROM products;",
    },
]
