{{ config(
    materialized = 'table',
) }}


SELECT
id:: INTEGER                    AS user_id,
firstName:: VARCHAR             AS first_name,
lastName:: VARCHAR              AS last_name,
age:: INTEGER                   AS age,
gender:: VARCHAR                AS gender,
email:: VARCHAR                 AS email,
address.city:: VARCHAR          AS city,
address.state:: VARCHAR         AS state,
address.country:: VARCHAR       AS country,
company.department:: VARCHAR    AS department,
company.title:: VARCHAR         AS job_title,
load_date::DATE                 AS load_date,
current_timestamp               AS _ingested_at,
current_date                    AS _ingested_date

From {{ source('bronze', 'bronze_trans_users') }}

