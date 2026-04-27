 {{ config(
    materialized = "table",
) }}


SELECT
product_id                  AS product_id,
product_title               AS product_title,
brand                       AS brand, 
product_category            AS category, 
product_price               AS product_price,

CASE
    WHEN product_price < 20 THEN 'Budget'
    WHEN product_price < 100 THEN 'Mid-Range'
    WHEN product_price < 500 THEN 'Premium'
    ELSE                          'Luxury'
END                         AS price_tier,

discounted_price            AS discounted_price,
product_rating              AS product_rating, 
stock                       AS stock, 
availability_status          AS stock_health, 

CASE 
    WHEN product_rating >= 4.5 THEN 'Excellent'
    WHEN product_rating >= 3.5 THEN 'Good'
    WHEN product_rating >= 2.5 THEN 'Average'
    ELSE                    'Poor'
END                        AS rating_band

from {{ref("silver_products")}}
