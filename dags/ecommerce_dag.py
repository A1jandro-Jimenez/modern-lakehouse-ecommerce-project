from airflow.sdk import dag, task
from datetime import datetime
from scripts.ingest_and_convert import fetch_and_upload

DBT_DIR = "/opt/airflow/duckdb_dbt_warehouse"
PROJECT_DIR = "/home/airflow/.dbt "

@dag(
    dag_id="lakehouse_pipeline",
    description="External ingest.py → S3 → dbt → MotherDuck",
    start_date=datetime(2026, 4, 23),
    catchup=False,
    schedule=None,
)
def lakehouse_pipeline():

    # ── INGEST ──────────────────────────────────────────────
    @task
    def fetch_and_upload_products():
        return fetch_and_upload("products", "products")

    @task
    def fetch_and_upload_users():
        return fetch_and_upload("users", "users")

    @task
    def fetch_and_upload_carts():
        return fetch_and_upload("carts", "carts")

    # ── DBT Bronze ─────────────────────────────────────────────────
    @task.bash
    def dbt_debug():
        return f"dbt debug --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"
    @task.bash
    def dbt_bronze_users_run():
        return f"dbt run --select bronze_trans_users --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"
    
    @task.bash
    def dbt_bronze_products_run():
        return f"dbt run --select bronze_trans_products --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"
    
    @task.bash
    def dbt_bronze_carts_run():
        return f"dbt run --select bronze_trans_carts --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"
    
    @task.bash
    def dbt_bronze_tests():
        # ← fixed: removed space after comma, fixed --project-dir typo
        return f"dbt test --select bronze_trans_carts bronze_trans_products bronze_trans_users --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"
    

    # ── DBT Silver ─────────────────────────────────────────────────

    @task.bash
    def dbt_silver_carts_run():
        return f"dbt run --select silver_carts --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"

    @task.bash
    def dbt_silver_products_run():
        return f"dbt run --select silver_products --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"

    @task.bash
    def dbt_silver_users_run():
        return f"dbt run --select silver_users --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"
    
    @task.bash
    def dbt_silver_tests():
        # ← fixed: removed space after comma, fixed --project-dir typo
        return f"dbt test --select silver_carts silver_products silver_users --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"
    

    # ── DBT Gold ─────────────────────────────────────────────────
    @task.bash
    def dbt_dim_products_run():
        return f"dbt run --select dim_products --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"

    @task.bash
    def dbt_dim_users_run():
        return f"dbt run --select dim_users --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"

    @task.bash
    def dbt_fct_orders_run():
        return f"dbt run --select fct_orders --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR} "
    
    @task.bash
    def dbt_fct_order_items_run():
        return f"dbt run --select fct_order_items --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"
    
    @task.bash
    def dbt_gold_tests():
        # ← fixed: removed space after comma, fixed --project-dir typo
        return f"dbt test --select dim_products dim_users fct_orders fct_order_items --profiles-dir {PROJECT_DIR} --project-dir {DBT_DIR}"


    # ── WIRING ───────────────────────────────────────────────
    ingest_products = fetch_and_upload_products()
    ingest_users    = fetch_and_upload_users()
    ingest_carts    = fetch_and_upload_carts()

    debug           = dbt_debug()
    bronze_products = dbt_bronze_products_run()
    bronze_users    = dbt_bronze_users_run()
    bronze_carts    = dbt_bronze_carts_run()
    bronze_tests    = dbt_bronze_tests()

    silver_carts    = dbt_silver_carts_run()
    silver_users    = dbt_silver_users_run()
    silver_products = dbt_silver_products_run()
    silver_tests    = dbt_silver_tests()

    gold_products   = dbt_dim_products_run()
    gold_users      = dbt_dim_users_run()
    gold_orders     = dbt_fct_orders_run()
    gold_order_items = dbt_fct_order_items_run()
    gold_tests      = dbt_gold_tests()


    # All ingest runs in parallel, then debug, then dbt models in parallel, then tests
    [ingest_products, ingest_users, ingest_carts] >> debug
    debug >> [bronze_users, bronze_products, bronze_carts] >> bronze_tests
    bronze_tests >> [silver_carts, silver_users, silver_products] >> gold_products >> gold_users
    gold_users>> gold_orders >> gold_order_items >> silver_tests >> gold_tests


lakehouse_pipeline()  # ← must be called with ()