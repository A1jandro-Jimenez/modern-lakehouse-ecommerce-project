{{ config(
    schema       = 'bronze',
) }}

SELECT 
*
From {{ source('external_s3', 'carts') }}

