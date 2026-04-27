{{ config
(materialized = 'table') 
}}

SELECT
    -- keys
    c.cart_id               AS order_id,
    c.user_id,
    c.product_id,

   -- product details (denormalised for convenience)
    p.product_title                 AS product_title,
    p.brand,
    p.category,


     -- line level financials
    c.product_quantity      AS quantity,
    c.product_price         AS unit_price,
    Round(c.product_price*c.product_quantity,2)   AS product_gross_total,
    c.discount_percentage,
    c.discounted_line_total AS line_net_total,
    ROUND(c.product_total- c.discounted_line_total, 2)       AS line_savings,
     
     -- line classifications
    CASE
        WHEN c.product_quantity >= 5 THEN 'bulk'
        WHEN c.product_quantity >= 2 THEN 'multi'
        ELSE                              'single item'
    END                                     AS line_quantity_band,


    CASE
        WHEN c.discount_percentage >= 20 THEN 'heavily discounted'
        WHEN c.discount_percentage >= 5  THEN 'lightly discounted'
        ELSE                                  'full price'
    END                                     AS discount_band

FROM {{ ref('silver_carts') }}          c
LEFT JOIN {{ ref('dim_products') }}     p ON c.product_id = p.product_id

