from sodapy import Socrata

import os
import json

from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

env_path = Path.cwd() / ".env"
load_dotenv(env_path)

api_token = os.getenv("NYC_API_TOKEN")
username = os.getenv("NYC_USERNAME")
password = os.getenv("NYC_PASSWORD")
DATASET = 'erm2-nwe9'




client = Socrata('data.cityofnewyork.us',
                 api_token,
                 username=username,
                 password=password,
                 timeout=180)
PAGE_SIZE = 1000  

def fetch_data(target_date: str | None = None) -> list[dict]:
    if target_date is None:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.000")

    all_rows = []
    offset = 0

    while True:
        page = client.get(
            DATASET,
            select="*",
            where=f"created_date > '{target_date}'",
            limit=PAGE_SIZE,
            offset=offset,
        )
        all_rows.extend(page)

        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    return all_rows

def write_raw(rows: list[dict], target_date: str) -> None:
    Path("data").mkdir(exist_ok=True)
    out_path = Path("data") / "_raw_extract.json"
    with open(out_path, "w") as f:
        json.dump({"target_date": target_date, "rows": rows}, f, indent=2)

def main():
    target_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT00:00:00.000")
    rows = fetch_data(target_date)
    write_raw(rows,target_date)
if __name__ == "__main__":
    main()