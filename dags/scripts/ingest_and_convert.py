import json, os, boto3, requests, duckdb, io
from datetime import datetime
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
S3_BUCKET = os.getenv("S3_BUCKET")

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)


def fetch_and_upload(endpoint, entity_name):
    base_url = f"https://dummyjson.com/{endpoint}"
    limit = 30
    skip = 0
    all_data = []

    while True:
        url = f"{base_url}?limit={limit}&skip={skip}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error fetching {entity_name}")
            break

        data = response.json()
        records = data.get(endpoint, [])

        if not records:
            break

        all_data.extend(records)
        skip += limit

    if not all_data:
        print(f"No data fetched for {entity_name}, skipping upload.")
        return

    # Write JSON to temp file and convert to Parquet via DuckDB
    os.makedirs("C:/tmp", exist_ok=True)
    tmp_json = f"C:/tmp/{entity_name}.json"
    tmp_parquet = f"C:/tmp/{entity_name}.parquet"

    with open(tmp_json, "w") as f:
        json.dump(all_data, f)

    con = duckdb.connect()
    con.execute(f"COPY (SELECT * FROM read_json_auto('{tmp_json}')) TO '{tmp_parquet}' (FORMAT PARQUET)")
    con.close()

    with open(tmp_parquet, "rb") as f:
        parquet_bytes = f.read()

    today = datetime.now().strftime("%Y-%m-%d")
    key = f"bronze/{entity_name}/load_date={today}/{entity_name}.parquet"

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=parquet_bytes
    )

    print(f"{entity_name} uploaded to s3://{S3_BUCKET}/{key}")


