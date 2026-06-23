
import csv
import datetime
import logging
import sys
import hashlib
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def calculate_entity_hash(content_id, keyword, country, device, search_type):
    s = f"{content_id or ''}|{keyword or ''}|{country or ''}|{device or ''}|{search_type or ''}"
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def classify_row(metrics):
    try:
        nonzero_365_pct = metrics.get('nonzero_click_days_365d_pct', 0)
        nonzero_730_pct = metrics.get('nonzero_click_days_730d_pct', 0)
        nonzero_90_pct = metrics.get('nonzero_click_days_90d_pct', 0)
        nonzero_365_30_pct = metrics.get('nonzero_click_days_365_minus_30_pct', 0)
        clicks_100_730_pct = metrics.get('clicks_gt_100_days_730d_pct', 0)
        is_seasonal = metrics.get('is_seasonal', 0)

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
    input_file = 'simulation_data.csv'
    data = []

    logging.info(f"Loading data from {input_file}...")

    with open(input_file, 'r', encoding='utf-8') as f:
        header_line = f.readline()
        f.seek(0)
        delimiter = '\t' if '\t' in header_line else ','
        reader = csv.DictReader(f, delimiter=delimiter)

        col_map = {
            'Date': 'date', 'LandingPage': 'content_id', 'DeviceCategory': 'device',
            'Country': 'country', 'SearchType': 'search_type', 'Clicks': 'clicks'
        }

        for row in reader:
            clean_row = {}
            for src, dest in col_map.items():
                val = row.get(src, '')
                if dest == 'clicks':
                    try:
                        clean_row[dest] = int(float(val)) if val else 0
                    except ValueError:
                        clean_row[dest] = 0
                elif dest == 'date':
                    clean_row[dest] = parse_date(val)
                else:
                    clean_row[dest] = val.strip()

            for k in ['content_id', 'device', 'country', 'search_type']:
                if k not in clean_row: clean_row[k] = ''

            clean_row['type'] = 'PAGE'
            clean_row['keyword'] = ''

            if clean_row['date']:
                data.append(clean_row)

    logging.info(f"Loaded {len(data)} rows.")

    entity_history = defaultdict(dict)
    for row in data:
        key = (row['content_id'], row['device'], row['country'], row['search_type'])
        entity_history[key][row['date']] = row['clicks']

    processed_rows = []
    logging.info("Calculating metrics and generating schema...")

    now_ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for row in data:
        target_date = row['date']
        key = (row['content_id'], row['device'], row['country'], row['search_type'])
        history = entity_history[key]

        def count_days(window_size, threshold_fn, offset_days=0):
            wd_end = target_date - datetime.timedelta(days=offset_days)
            wd_start = wd_end - datetime.timedelta(days=window_size - 1)
            count = 0
            curr = wd_start
            while curr <= wd_end:
                 clicks = history.get(curr, 0)
                 if threshold_fn(clicks): count += 1
                 curr += datetime.timedelta(days=1)
            return count

        nz_365 = count_days(365, lambda c: c > 0)
        nz_730 = count_days(730, lambda c: c > 0)
        nz_90 = count_days(90, lambda c: c > 0)
        gt100_730 = count_days(730, lambda c: c > 100)
        nz_365_30 = count_days(365, lambda c: c > 0, offset_days=30)

        metrics = {
            'nonzero_click_days_365d_pct': round(nz_365 / 365.0, 4),
            'nonzero_click_days_730d_pct': round(nz_730 / 730.0, 4),
            'nonzero_click_days_90d_pct': round(nz_90 / 90.0, 4),
            'clicks_gt_100_days_730d_pct': round(gt100_730 / 730.0, 4),
            'nonzero_click_days_365_minus_30_pct': round(nz_365_30 / 365.0, 4),
            'is_seasonal': 0
        }

        classification = classify_row(metrics)

        entity_hash = calculate_entity_hash(
            row['content_id'], row['keyword'], row['country'], row['device'], row['search_type']
        )

        out_row = {
            'entity_hash': entity_hash,
            'date': row['date'],
            'type': row['type'],
            'content_id': row['content_id'],
            'keyword': row['keyword'],
            'country': row['country'],
            'device': row['device'],
            'search_type': row['search_type'],
            'evergreen_class': classification,
            'active_flag': True,
            'scd_start_dt': now_ts,
            'scd_end_dt': None,
            'version_no': 1,
            'etl_insert_ts': now_ts,
            'metric_365d': metrics['nonzero_click_days_365d_pct']
        }
        processed_rows.append(out_row)

    processed_rows.sort(key=lambda x: (x['date'], x['entity_hash']), reverse=True)

    display_cols = [
        'entity_hash', 'date', 'type', 'content_id', 'keyword', 'country', 'device', 'search_type',
        'evergreen_class', 'active_flag', 'scd_start_dt', 'scd_end_dt', 'version_no'
    ]

    print("\t".join(display_cols))

    match_count = 0
    for r in processed_rows:
        if match_count < 100:
             vals = [str(r.get(c, 'NULL')) for c in display_cols]
             print("\t".join(vals))
             match_count += 1
        else:
            break

    with open('simulation_results_full_schema.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=display_cols + ['metric_365d'], delimiter='\t')
        writer.writeheader()
        for r in processed_rows:
            writer.writerow({k: r.get(k, '') for k in display_cols + ['metric_365d']})

    logging.info("Simulation finished.")

if __name__ == "__main__":
    run_simulation()
