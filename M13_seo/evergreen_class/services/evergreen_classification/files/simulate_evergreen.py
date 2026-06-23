
import pandas as pd
import numpy as np
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def classify_row(row):
    try:
        nonzero_365_pct = row.get('nonzero_click_days_365d_pct', 0)
        nonzero_730_pct = row.get('nonzero_click_days_730d_pct', 0)
        nonzero_90_pct = row.get('nonzero_click_days_90d_pct', 0)
        nonzero_365_30_pct = row.get('nonzero_click_days_365_minus_30_pct', 0)
        clicks_100_730_pct = row.get('clicks_gt_100_days_730d_pct', 0)
        is_seasonal = row.get('is_seasonal', 0)

        if nonzero_365_pct >= 0.95:
            if nonzero_730_pct >= 0.95:
                if clicks_100_730_pct >= 0.95:
                    return "Top-Evergreen"
                else:
                    return "Evergreen"
            else:
                return "Top Annual Theme"
        else:
            if nonzero_90_pct >= 0.95:
                return "Evergreen-Prospect"
            else:
                if nonzero_365_30_pct >= 0.95:
                    return "Ex-Evergreen"
                else:
                    if is_seasonal:
                        return "Seasonal Evergreen"
                    else:
                        return "Not Evergreen"
    except Exception as e:
        logging.error(f"Classification error: {e}")
        return "Error"

def run_simulation():
    logging.info("Loading data from simulation_data.csv...")
    try:
        df_raw = pd.read_csv('simulation_data.csv', sep='\t')
        if len(df_raw.columns) <= 1:
             df_raw = pd.read_csv('simulation_data.csv', sep=',')
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        return

    col_map = {
        'Date': 'date',
        'LandingPage': 'content_id',
        'DeviceCategory': 'device',
        'Country': 'country',
        'SearchType': 'search_type',
        'Clicks': 'clicks',
        'is_final': 'is_final'
    }

    df = df_raw.rename(columns=col_map)
    df['date'] = pd.to_datetime(df['date'])
    df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)

    for col in ['content_id', 'device', 'country', 'search_type']:
        if col in df.columns:
             df[col] = df[col].astype(str).str.strip()

    logging.info(f"Loaded {len(df)} rows. Unique Dates: {df['date'].unique()}")

    target_date = df['date'].max()
    start_date = target_date - pd.Timedelta(days=729)

    logging.info(f"Simulation Target Date: {target_date.date()}")
    logging.info(f"Generating scaffold from {start_date.date()} to {target_date.date()} (730 days)...")

    entity_cols = ['content_id', 'device', 'country', 'search_type']
    entities = df[entity_cols].drop_duplicates()

    all_dates = pd.DataFrame({'date': pd.date_range(start=start_date, end=target_date, freq='D')})

    entities['_key'] = 1
    all_dates['_key'] = 1
    scaffold = pd.merge(entities, all_dates, on='_key').drop('_key', axis=1)

    full_df = pd.merge(scaffold, df, on=['content_id', 'device', 'country', 'search_type', 'date'], how='left')
    full_df['clicks'] = full_df['clicks'].fillna(0)

    logging.info(f"Scaffolded Data Size: {len(full_df)} rows")

    full_df = full_df.sort_values(by=entity_cols + ['date'])
    full_df['is_nonzero'] = (full_df['clicks'] > 0).astype(int)
    full_df['is_gt_100'] = (full_df['clicks'] > 100).astype(int)

    logging.info("Calculating Rolling Metrics...")

    full_df['nonzero_days_365'] = full_df.groupby(entity_cols)['is_nonzero'].transform(
        lambda x: x.rolling(window=365, min_periods=0).sum()
    )

    full_df['nonzero_days_730'] = full_df.groupby(entity_cols)['is_nonzero'].transform(
        lambda x: x.rolling(window=730, min_periods=0).sum()
    )

    full_df['nonzero_days_90'] = full_df.groupby(entity_cols)['is_nonzero'].transform(
        lambda x: x.rolling(window=90, min_periods=0).sum()
    )

    full_df['gt_100_days_730'] = full_df.groupby(entity_cols)['is_gt_100'].transform(
        lambda x: x.rolling(window=730, min_periods=0).sum()
    )

    full_df['nonzero_days_395'] = full_df.groupby(entity_cols)['is_nonzero'].transform(
        lambda x: x.rolling(window=395, min_periods=0).sum()
    )
    full_df['nonzero_days_30'] = full_df.groupby(entity_cols)['is_nonzero'].transform(
        lambda x: x.rolling(window=30, min_periods=0).sum()
    )
    full_df['nonzero_days_365_shifted'] = full_df['nonzero_days_395'] - full_df['nonzero_days_30']

    full_df['nonzero_click_days_365d_pct'] = full_df['nonzero_days_365'] / 365.0
    full_df['nonzero_click_days_730d_pct'] = full_df['nonzero_days_730'] / 730.0
    full_df['nonzero_click_days_90d_pct'] = full_df['nonzero_days_90'] / 90.0
    full_df['clicks_gt_100_days_730d_pct'] = full_df['gt_100_days_730'] / 730.0
    full_df['nonzero_click_days_365_minus_30_pct'] = full_df['nonzero_days_365_shifted'] / 365.0

    full_df['is_seasonal'] = 0

    metric_cols = [
        'nonzero_click_days_365d_pct',
        'nonzero_click_days_730d_pct',
        'nonzero_click_days_90d_pct',
        'nonzero_click_days_365_minus_30_pct',
        'clicks_gt_100_days_730d_pct'
    ]
    for col in metric_cols:
        full_df[col] = full_df[col].round(4)

    target_dates = df['date'].unique()
    final_output = full_df[full_df['date'].isin(target_dates)].copy()

    logging.info("Applying Classification Decision Tree...")
    final_output['evergreen_class'] = final_output.apply(classify_row, axis=1)

    display_cols = [
        'date', 'content_id', 'device', 'country', 'search_type',
        'evergreen_class',
        'clicks',
        'nonzero_click_days_365d_pct',
        'nonzero_click_days_90d_pct',
        'nonzero_click_days_365_minus_30_pct'
    ]

    final_output = final_output.sort_values(by=['date', 'content_id'], ascending=[False, True])

    output_filename = 'simulation_results.csv'
    final_output[display_cols].to_csv(output_filename, index=False, sep='\t')
    logging.info(f"Simulation Complete. Results saved to {output_filename}")

    try:
        print(final_output[display_cols].head(20).to_markdown(index=False))
    except ImportError:
        print(final_output[display_cols].head(20).to_string(index=False))

if __name__ == "__main__":
    run_simulation()
