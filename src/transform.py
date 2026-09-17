import json
import logging
import sys
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("transform")

REQUIRED_COLUMNS = {"unique_key", "created_date", "complaint_type","community_board"}


def load_raw() -> dict:
    with open(Path("data") / "_raw_extract.json") as f:
        return json.load(f)


def transform(payload: dict) -> pd.DataFrame:
    target_date = payload["target_date"]
    rows = payload["rows"]

    df = pd.DataFrame(rows)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"API response is missing expected columns: {missing}")

    df["complaint_type"] = df["complaint_type"].fillna("UNKNOWN").str.strip()
    df["community_board"] = df["community_board"].fillna("UNKNOWN").str.strip()

    return df,target_date

def summarize(df,target_date):

    summary = (
        df.groupby(["borough","complaint_type"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    summary["date"] = target_date
    summary["ingested_at"] = pd.Timestamp.now('UTC').isoformat()

    return summary


def validate_summary(summary: pd.DataFrame, raw_row_count: int) -> None:
    if summary.empty:
        raise ValueError("Transform produced zero rows")

    total = int(summary["count"].sum())
    if total != raw_row_count:
        raise ValueError(f"Row count mismatch: {total} summarized vs {raw_row_count} raw")

    if total < 500:
        raise ValueError(f"Low total complaint count: {total}")

    unknown_share_ct = summary.loc[summary["complaint_type"] == "UNKNOWN", "count"].sum() / total
    if unknown_share_ct > 0.5:
        raise ValueError(f"Too many UNKNOWN complaint types: {unknown_share_ct:.0%}")


    logger.info("Validation passed: %d complaint types, %d total complaints", len(summary), total)

def validate_geo_summary(summary: pd.DataFrame) -> None:
    if summary.empty:
        raise ValueError("Transform produced zero rows")

    total = int(summary["count"].sum())

    unknown_share_cb = summary.loc[summary["community_board"] == "UNKNOWN", "count"].sum() / total
    if unknown_share_cb > 0.5:
        raise ValueError(f"Too many UNKNOWN complaint types: {unknown_share_cb:.0%}")


    logger.info("Validation passed: %d community_boards, %d total complaints", len(summary), total)

def geographic_summary(df,target_date):

    
    geo_summary = (
        df.groupby(["community_board",'complaint_type'])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    geo_summary["date"] = target_date
    geo_summary["ingested_at"] = pd.Timestamp.now('UTC').isoformat()

    return geo_summary


def main():
    payload = load_raw()
    df,target_date = transform(payload)
    summary = summarize(df,target_date)
    geo_summary = geographic_summary(df,target_date)
    
    try:
        validate_summary(summary, raw_row_count=len(payload["rows"]))
        validate_geo_summary(geo_summary)
    except ValueError as e:
        logger.error("Data quality check failed: %s", e)
        sys.exit(1)

    Path("data").mkdir(exist_ok=True)
    summary.to_csv("data/_complaint_type_daily.csv", index = False)
    geo_summary.to_csv('data/_community_board_daily.csv',index=False)
    logger.info("Wrote %d cleaned rows", len(summary))
    logger.info("Wrote %d community boards rows", len(geo_summary))


if __name__ == "__main__":
    main()