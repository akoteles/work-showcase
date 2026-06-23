#!/usr/bin/env python

import os
from api import AnalyticsPlatformAPI
from bigquery import BigQuery
import pandas as pd
import numpy as np
import logging
from helpers import get_secret
from datetime import datetime, timedelta
from config import (
    DATAPOOL_BIGQUERY_SA,
    ANALYTICS_PLATFORM_QUERIES,
    ACCOUNT_ANALYTICS_PLATFORM_MAPPINGS,
    BQ_ANALYTICS_PLATFORM_COLUMNS,
    BQ_ANALYTICS_PLATFORM_STR_COLUMNS,
    BQ_ANALYTICS_PLATFORM_INT_COLUMNS,
    BQ_ANALYTICS_PLATFORM_FLOAT_COLUMNS,
    BQ_ANALYTICS_PLATFORM_CALCULATED_COLUMNS,
    BQ_SEARCH_TRAFFIC_COLUMNS,
    ACCOUNT_DISCOVER_MAPPINGS,
    BQ_DISCOVER_COLUMNS,
    BQ_DISCOVER_INT_COLUMNS,
    BQ_DISCOVER_FLOAT_COLUMNS,
    BQ_DISCOVER_CALCULATED_COLUMNS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def normalize_date(df: pd.DataFrame, column="Date"):
    """Generic date cleaner"""
    if column in df.columns:
        df[column] = pd.to_datetime(df[column], errors="coerce").dt.normalize()
    else:
        df[column] = pd.NaT
    return df


def ensure_numeric(df: pd.DataFrame, columns: list, default=np.nan):
    """Generic numeric converter"""
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = pd.Series([default] * len(df), index=df.index)
    return df


def map_all_data_columns(df: pd.DataFrame, account_name: str) -> pd.DataFrame:
    """
    Maps and transforms column names and data types for consistency
    before loading into BigQuery. Handles int, float, string columns,
    special account-specific transformations, and calculated metrics.

    Args:
        df (pd.DataFrame): The input DataFrame with raw data.

    Returns:
        pd.DataFrame: The transformed DataFrame with renamed columns and standardized data types.
    """
    account_schema = ACCOUNT_ANALYTICS_PLATFORM_MAPPINGS[account_name]
    logging.info(f"Mapping for '{account_name}' is {account_schema}")

    df = df.rename(columns=account_schema)
    df = normalize_date(df, "Date")
    df = ensure_numeric(df, BQ_ANALYTICS_PLATFORM_INT_COLUMNS[account_name])
    df = ensure_numeric(df, BQ_ANALYTICS_PLATFORM_FLOAT_COLUMNS[account_name])

    if account_name == "Account1":
        if "page_chapter1" in df.columns and "page_chapter2" in df.columns:
            df["Category"] = df.apply(
                lambda row: (
                    row["page_chapter2"]
                    if str(row["page_chapter1"]).lower() == "videos"
                    else row["page_chapter1"]
                ),
                axis=1,
            )
        elif "page_chapter1" in df.columns:
            df["Category"] = df["page_chapter1"]
        elif "page_chapter2" in df.columns:
            df["Category"] = df["page_chapter2"]
        else:
            df["Category"] = np.nan

    for calc in BQ_ANALYTICS_PLATFORM_CALCULATED_COLUMNS[account_name]:
        output_col = calc.get("output")
        numerator = calc.get("numerator")
        denominators = calc.get("denominator_fallbacks", [calc.get("denominator")])

        if numerator not in df.columns:
            df[output_col] = np.nan
            continue

        denominator_col = next((col for col in denominators if col in df.columns), None)
        if denominator_col:
            df[denominator_col] = pd.to_numeric(df[denominator_col], errors="coerce")
            df[output_col] = df[numerator] / df[denominator_col]
        else:
            df[output_col] = np.nan

    for col in BQ_ANALYTICS_PLATFORM_COLUMNS[account_name]:
        if col not in df.columns:
            df[col] = np.nan

    for col in BQ_ANALYTICS_PLATFORM_STR_COLUMNS[account_name]:
        df[col] = df[col].astype("string")

    return df[BQ_ANALYTICS_PLATFORM_COLUMNS[account_name]]


def map_search_traffic_data(df: pd.DataFrame, account_name: str) -> pd.DataFrame:
    """
    Maps and transforms search traffic data.

    Args:
        df (pd.DataFrame): The input DataFrame with raw data.

    Returns:
        pd.DataFrame: The transformed DataFrame with renamed columns and standardized data types.
    """
    logging.info(
        f"Mapping for '{account_name}' is "
        f"{{'date': 'Date', 'src': 'TrafficSource', 'm_visits': 'Visits'}}"
    )
    df = df.rename(
        columns={"date": "Date", "src": "TrafficSource", "m_visits": "Visits"}
    )
    df = normalize_date(df, "Date")
    df = ensure_numeric(df, ["Visits"], default=np.nan)

    for col in BQ_SEARCH_TRAFFIC_COLUMNS[account_name]:
        if col not in df.columns:
            df[col] = np.nan

    return df[BQ_SEARCH_TRAFFIC_COLUMNS[account_name]]


def map_discover_data(df: pd.DataFrame, account_name: str) -> pd.DataFrame:
    """
    Generic mapping function for Discover, with special handling for Account6 (+ Search traffic share).

    Args:
        account_name (str): Name of account based on which bigquery schema is considered
        df (pd.DataFrame): The input DataFrame with raw data.

    Returns:
        pd.DataFrame: The transformed DataFrame with renamed columns and standardized data types.
    """

    account_schema = ACCOUNT_DISCOVER_MAPPINGS[account_name]
    logging.info(f"Mapping for '{account_name}' is {account_schema}")

    df = df.rename(columns=account_schema)
    df = normalize_date(df, "Date")
    df = ensure_numeric(df, BQ_DISCOVER_INT_COLUMNS[account_name])
    df = ensure_numeric(df, BQ_DISCOVER_FLOAT_COLUMNS[account_name])

    for calc_col, rules in BQ_DISCOVER_CALCULATED_COLUMNS[account_name].items():
        num = rules["numerator"]
        denom_primary = rules["denominator_primary"]
        denom_fallback = rules["denominator_fallback"]

        num_series = (
            pd.to_numeric(df[num], errors="coerce")
            if num in df
            else pd.Series(np.nan, index=df.index)
        )
        denom_primary_series = (
            pd.to_numeric(df[denom_primary], errors="coerce")
            if denom_primary in df
            else pd.Series(np.nan, index=df.index)
        )
        denom_fallback_series = (
            pd.to_numeric(df[denom_fallback], errors="coerce")
            if denom_fallback in df
            else pd.Series(np.nan, index=df.index)
        )

        df[calc_col] = np.where(
            denom_primary_series > 0,
            num_series / denom_primary_series,
            np.where(
                denom_fallback_series > 0,
                num_series / denom_fallback_series,
                np.nan,
            ),
        )

    for col in BQ_DISCOVER_COLUMNS[account_name]:
        if col not in df.columns:
            df[col] = np.nan

    return df[BQ_DISCOVER_COLUMNS[account_name]]


def main():
    """
    Main function to extract data from AnalyticsPlatform API, transform it,
    and load it into BigQuery.
    """
    account_name = os.getenv("ACCOUNT_NAME")

    FUNCTION_TABLE_API_MAPPING = {
        "Account6": {
            "get_all_data": {
                "table": os.getenv("BQ_TABLE_ANALYTICS_PLATFORM_ALL_DATA"),
                "api_key": "API_KEY_ALL_DATA",
            },
            "get_search_traffic_data": {
                "table": os.getenv("BQ_TABLE_ANALYTICS_PLATFORM_SEARCH_TRAFFIC_DATA"),
                "api_key": "API_KEY_SEARCH_TRAFFIC_DATA",
            },
            "get_discover_data": {
                "table": os.getenv("BQ_TABLE_ANALYTICS_PLATFORM_DISCOVER_DATA"),
                "api_key": "API_KEY_DISCOVER_DATA",
            },
        },
        "_default": {
            "get_all_data": {
                "table": os.getenv("BQ_TABLE_ANALYTICS_PLATFORM_ALL_DATA"),
                "api_key": "API_KEY",
            },
            "get_search_traffic_data": {
                "table": os.getenv("BQ_TABLE_ANALYTICS_PLATFORM_SEARCH_TRAFFIC_DATA"),
                "api_key": "API_KEY",
            },
            "get_discover_data": {
                "table": os.getenv("BQ_TABLE_ANALYTICS_PLATFORM_DISCOVER_DATA"),
                "api_key": "API_KEY",
            },
        },
    }
    account_mapping = FUNCTION_TABLE_API_MAPPING.get(
        account_name, FUNCTION_TABLE_API_MAPPING["_default"]
    )

    logging.info(f"Starting AnalyticsPlatform data extraction process for '{account_name}'...")
    start_tmstp = (datetime.utcnow() - timedelta(days=0)).strftime("%Y-%m-%d")
    end_tmstp = (datetime.utcnow() - timedelta(days=0)).strftime("%Y-%m-%d")
    logging.info(f"Date range: {start_tmstp} to {end_tmstp}")

    bq_client = BigQuery(
        service_account_info=DATAPOOL_BIGQUERY_SA,
        project_id=os.getenv("DATAPOOL_PROJECT_ID"),
    )

    for query_key, config in account_mapping.items():
        try:
            table_name = config["table"]
            api_key_env = config["api_key"]

            logging.info(f"Fetching '{query_key}' for '{account_name}'...")

            api_key = get_secret(
                os.getenv(api_key_env), os.getenv("GCP_SECRET_PROJECT_ID")
            )
            analytics_platform = AnalyticsPlatformAPI(
                api_key,
                start_tmstp=start_tmstp,
                end_tmstp=end_tmstp,
            )

            data_query = ANALYTICS_PLATFORM_QUERIES[account_name][query_key]
            data_query["period"]["p1"][0].update(
                {"start": start_tmstp, "end": end_tmstp}
            )
            data = analytics_platform.pagination_get_data(data_query)

            if data:
                data_df = pd.DataFrame(data)
                if query_key == "get_all_data":
                    data_df = map_all_data_columns(data_df, account_name)
                elif query_key == "get_search_traffic_data":
                    data_df = map_search_traffic_data(data_df, account_name)
                else:
                    data_df = map_discover_data(data_df, account_name)

                data_df["export_timestamp"] = pd.to_datetime("now")
                logging.info(
                    f"Data fetched for '{account_name}'. Total records: {len(data_df)}"
                )

                bq_client.load_data(
                    dataset_name=os.getenv("DATAPOOL_BQ_DATASET"),
                    table_name=table_name,
                    dataframe=data_df,
                )
            else:
                logging.info(f"No data fetched for {account_name}.")
        except Exception as e:
            logging.error(f"Error fetching {query_key} for {account_name}: {e}")


if __name__ == "__main__":
    main()
