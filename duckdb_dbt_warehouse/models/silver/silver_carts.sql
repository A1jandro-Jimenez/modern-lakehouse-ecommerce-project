 {{ config(
    materialized = 'table',
    unique_key   = ['cart_id', 'product_id'] 
) }}

SELECT
    -- cart level fields
    id::INTEGER                        AS cart_id,
    userId::INTEGER                    AS user_id,
    total::DOUBLE PRECISION            AS cart_total,
    discountedTotal::DOUBLE PRECISION  AS cart_discounted_total,
    totalProducts::INTEGER             AS cart_total_products,
    totalQuantity::INTEGER             AS cart_total_quantity,
    
    -- unnested product fields — one row per product
    p.id::INTEGER                       AS product_id,
    p.title::VARCHAR                    AS product_title,
    p.price:: DOUBLE PRECISION          AS product_price,
    p.quantity::INTEGER                 AS product_quantity,
    p.total::DOUBLE PRECISION           AS product_total,
    p.discountPercentage::DOUBLE PRECISION AS discount_percentage,
    p.discountedTotal::DOUBLE PRECISION          AS  discounted_line_total,
    p.thumbnail::VARCHAR                AS thumbnail,
    
    -- metadata
    load_date::DATE                    AS load_date,
    current_timestamp                   AS _ingested_at,
    current_date                        AS _ingested_date


FROM {{ source('bronze', 'bronze_trans_carts') }}
CROSS JOIN unnest(products) AS t(p)



                