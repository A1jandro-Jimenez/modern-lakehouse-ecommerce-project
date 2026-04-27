{{ config(materialized = 'table') }}

SELECT
    user_id,
    first_name || ' ' || last_name   AS full_name,
    email                            AS email,
    age                              AS age,
    case
        when age < 25 then '18-24'
        when age < 35 then '25-34'
        when age < 45 then '35-44'
        when age < 55 then '45-54'
        else '55+'
    end                             AS age_band,
    gender                          AS gender,
    city                            AS city,
    state                           AS state,
    country                         AS country, 
    department                      AS department,
    job_title                       AS job_title

FROM {{ ref('silver_users') }}
