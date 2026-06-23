#!/usr/bin/env python

import os
import json
import logging
import pandas as pd
from datetime import datetime, timedelta
from api import SearchConsoleAPI
from bigquery import BigQuery
from helpers import get_secret
from config import SEARCH_TYPES, SCOPES, DATA_POOL_BIGQUERY_SA, MAX_DATA_AGE_DAYS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    account_name = os.getenv("ACCOUNT_NAME")
    account_gsc_sa = json.loads(
        get_secret(os.getenv("GSC_SA"), os.getenv("GCP_SECRET_PROJECT_ID"))
    )
    account_bq_table = os.getenv("BQ_TABLE_GSC")

    bq_client = BigQuery(
        service_account_info=DATA_POOL_BIGQUERY_SA,
        project_id=os.getenv("DATA_POOL_PROJECT_ID"),
    )
    gsc_api = SearchConsoleAPI(service_account_info=account_gsc_sa, scopes=SCOPES)
    dataset = os.getenv("DATA_POOL_BQ_DATASET")

    url_properties = gsc_api.get_url_properties()
    today = datetime.today().date()

    logging.info("Phase 1: Re-fetching finalized data for is_final = False")
    unfinalized_dates = bq_client.get_unfinalized_dates(dataset, account_bq_table)
    if not unfinalized_dates:
        logging.info("No unfinalized dates found — skipping Phase 1 re-fetch.")
    else:
        for fetch_date in sorted(unfinalized_dates):
            all_data = []
            for site_url in url_properties:
                for search_type in SEARCH_TYPES:
                    rows = gsc_api.fetch_data(
                        site_url,
                        str(fetch_date),
                        str(fetch_date),
                        search_type,
                        data_state="final",
                    )

                    if rows:
                        logging.info(
                            f"Fetching FINAL data for {fetch_date} [{search_type}]"
                        )
                        for row in rows:
                            keys = row["keys"]
                            row_data = {
                                "Date": keys[0],
                                "LandingPage": keys[1],
                                "SearchType": search_type,
                                "Clicks": row.get("clicks", 0),
                                "Impressions": row.get("impressions", 0),
                                "SiteCTR": row.get("ctr", 0) * 100,
                                "AveragePosition": row.get("position", 0),
                                "DeviceCategory": (
                                    None if search_type == "Discover" else keys[2]
                                ),
                                "Country": (
                                    keys[2] if search_type == "Discover" else keys[3]
                                ),
                                "is_final": True,
                            }
                            all_data.append(row_data)
                    else:
                        logging.info(f"No data for {fetch_date} [{search_type}]")

            if all_data:
                df = pd.DataFrame(all_data)
                df["Date"] = pd.to_datetime(df["Date"])
                bq_client.delete_rows_by_dates(
                    dataset, account_bq_table, df["Date"].dt.date.unique()
                )
                bq_client.load_data(dataset, account_bq_table, df)

    logging.info("Phase 2: Ingesting new data (dataState = all)")
    last_3_days = [(today - timedelta(days=i)) for i in range(3)]
    max_date = bq_client.get_most_current_date(dataset, account_bq_table)
    logging.info(f"Max Date - {max_date}")
    last_finalized_date = bq_client.get_last_finalized_date(dataset, account_bq_table)
    logging.info(f"Last Finalized Date - {last_finalized_date}")
    if max_date in last_3_days:
        logging.info("Max date is within last 3 days")
        if last_finalized_date:
            last_3_days = [date for date in last_3_days if date > last_finalized_date]
            logging.info(f"Updated Last 3 Dates - {last_3_days}")
        max_date = min(last_3_days) - timedelta(days=1)
        logging.info(f"max_date is within the last 3 days; resetting to: {max_date}")
    start_date = (
        (max_date + timedelta(days=1))
        if max_date
        else today - timedelta(days=MAX_DATA_AGE_DAYS)
    )
    last_3_days = [d.strftime("%Y-%m-%d") for d in last_3_days]
    while start_date <= today:
        for site_url in url_properties:
            for search_type in SEARCH_TYPES:
                logging.info(f"Fetching ALL data for {start_date} [{search_type}]")
                rows = gsc_api.fetch_data(
                    site_url,
                    str(start_date),
                    str(start_date),
                    search_type,
                    data_state="all",
                )
                all_data = []

                if rows:
                    logging.info(
                        f"Fetching Latest data for {start_date} [{search_type}]"
                    )
                    for row in rows:
                        keys = row["keys"]
                        row_data = {
                            "Date": keys[0],
                            "LandingPage": keys[1],
                            "SearchType": search_type,
                            "Clicks": row.get("clicks", 0),
                            "Impressions": row.get("impressions", 0),
                            "SiteCTR": row.get("ctr", 0) * 100,
                            "AveragePosition": row.get("position", 0),
                            "DeviceCategory": (
                                None if search_type == "Discover" else keys[2]
                            ),
                            "Country": (
                                keys[2] if search_type == "Discover" else keys[3]
                            ),
                            "is_final": False,
                        }
                        all_data.append(row_data)
                else:
                    logging.info(f"No data for '{search_type}' at '{site_url}'")

                if all_data:
                    if str(start_date) in last_3_days:
                        bq_client.delete_rows_by_dates(
                            dataset, account_bq_table, [str(start_date)], search_type
                        )
                    logging.info(f"Inserting all data for {start_date} [{search_type}]")
                    df = pd.DataFrame(all_data)
                    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
                    bq_client.load_data(dataset, account_bq_table, df)

        start_date += timedelta(days=1)


if __name__ == "__main__":
    main()
