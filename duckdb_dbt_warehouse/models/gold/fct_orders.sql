{{ 
    config(materialized = 'table') 
}}

SELECT
    -- keys
    cart_id                 AS order_id,
    user_id,


    -- financials (cart level totals only)
    cart_total              AS order_gross_total,
    cart_discounted_total   AS order_net_total,
    ROUND(cart_total
        - cart_discounted_total, 2)         AS total_savings,
    ROUND((cart_total - cart_discounted_total)
        / NULLIF(cart_total, 0) * 100, 2)   AS savings_pct,

    -- order size
    cart_total_products          AS distinct_products,
    cart_total_quantity          AS total_items,
    ROUND(cart_discounted_total
        / NULLIF(cart_total_quantity, 0), 2)     AS avg_item_value,

    -- classifications
    CASE
        WHEN cart_discounted_total >= 500 THEN 'high value'
        WHEN cart_discounted_total >= 100 THEN 'mid value'
        ELSE                                   'low value'
    END                                     AS order_value_band,

    CASE
        WHEN total_items >= 10 THEN 'bulk'
        WHEN total_items >= 5  THEN 'standard'
        ELSE                           'small'
    END                                     AS order_size_band

FROM {{ ref('silver_carts') }}
-- collapse product rows back to one row per cart
GROUP BY ALL