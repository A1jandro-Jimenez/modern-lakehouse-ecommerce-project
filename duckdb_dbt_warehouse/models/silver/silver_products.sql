 {{ config(
    materialized = 'table',
) }}


SELECT

id::INTEGER                                      As product_id,
title::VARCHAR                                   As product_title,
category::VARCHAR                                AS product_category,
price::DOUBLE PRECISION                          AS product_price,
discountPercentage::DOUBLE PRECISION             AS discount_percentage,
round(product_price * (1 - discount_percentage/ 100), 2)
                                                 AS discounted_price,

rating:: DOUBLE PRECISION                        AS product_rating,
stock::INTEGER                                   AS stock,
brand::VARCHAR                                   AS brand,
availabilityStatus::VARCHAR                      AS availability_status,
thumbnail:: VARCHAR                              AS thumbnail,

load_date:: DATE                                 As load_date,
current_timestamp                   AS _ingested_at,
current_date                        AS _ingested_date  

FROM {{ source('bronze', 'bronze_trans_products') }}                     