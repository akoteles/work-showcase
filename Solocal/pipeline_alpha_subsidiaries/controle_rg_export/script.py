import csv
import io
import json
import os
import subprocess
import sys
import traceback

from google.cloud import bigquery

from utils import files_to_treat, markTreated

date = os.getenv("SOURCE_DATE")
bqProject = os.getenv("BQ_PROJECT")
bqDataset = os.getenv("BQ_DATASET")
bqRegion = os.getenv("BQ_REGION")
code_filiale=os.getenv("CODE_FILIALE")


TASK_NAME = "CONTROLES_RG_EXPORT"
export_path = os.getenv("EXPORT_PATH")
export_path_gcs = os.getenv("EXPORT_GCS_PATH")
bq = bigquery.Client()
files = files_to_treat(bq, TASK_NAME)

with open("/app/6A_SQL_PALP_SALES_TRANSACTIONS_SUBSIDIARIES_REJETS_REGLES_GESTION.sql", encoding="UTF-8") as fd:
    query = fd.read()
rejets_fields = ['no_etab', 'li_rs', 'no_etab_nego', 'no_coml', 'li_origine_vente', 'da_souscr', 'da_valid_vente',
                 'da_facturation', 'num_article', 'co_produit', 'li_produit', 'mt_ht', 'mt_affranchis', 'no_top_annul',
                 'li_nom_vendeur', 'li_prenom_vendeur', 'duree_engagement', 'mt_ft', 'taux_fg', 'li_flag_deleted']

for f in files :
    if (f.cd_filiale==code_filiale):
        try:
            print("Export Ctrl_RG for: " + f.source)

            da_event_str = f.da_event.strftime('%Y-%m-%d')
            q = query.format(
                project_id=bqProject,
                dataset_id=bqDataset,
                co_filiale=f.cd_filiale,
                da_event=da_event_str,
                no_flag_deleted='1'
            )
            print(q)
            res = bq.query(q)
            res.result()
            if res.error_result is None:
                file_name = "/tmp/PALP_TXT_REJETS_{filiale}_{da_event}.txt".format(filiale=f.cd_filiale,
                                                                                da_event=da_event_str)
                with open(file_name, encoding="UTF-8", mode="w") as fd:
                    cw = csv.DictWriter(fd, rejets_fields, delimiter=";")
                    cw.writeheader()
                    for row in res:
                        cw.writerow({x: row[x] for x in row.keys()})
                subprocess.check_call(["/usr/local/bin/rclone",
                                    "--config=/var/secrets/rclone/rclone.conf",
                                    "--verbose=4",
                                    "copy",
                                    file_name,
                                    export_path_gcs
                                    ])
                if export_path is not None and export_path != "":
                    subprocess.check_call(["/usr/local/bin/rclone",
                                        "--config=/var/secrets/rclone/rclone.conf",
                                        "--verbose=4",
                                        "--ftp-concurrency=1",
                                        "--dry-run",
                                        "copy",
                                        file_name, "{}/".format(export_path)])
                    markTreated(bq, f, TASK_NAME, date=date)
                else:
                    print("Error exporting for: " + f.source + " " + str(res.errors))
                    markTreated(bq, f, TASK_NAME, date=date, success=False,
                                comment=json.dumps(res.errors))
        except Exception as err:
            out = io.StringIO()
            traceback.print_tb(err.__traceback__, file=out)
            err = out.getvalue()
            print(sys.exc_info()[0])
            print(err)
            markTreated(bq, f, TASK_NAME, date=date, success=False,
                        comment=json.dumps(str(sys.exc_info()[0])))
