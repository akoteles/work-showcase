from airflow.models import Variable, DAG

from datetime import datetime, timedelta

from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.trigger_rule import TriggerRule

from commercial.utils.airflow import ChildDagOperator, run_python_with_context
from commercial.utils import read_file, pyrunner

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 3, 18),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'catchup': False,
    'retry_delay': timedelta(minutes=5),
}
RETRIES = 1
ENV = Variable.get('ENV')

if ENV.upper() == 'DEV':
    schedule = None
else:
    schedule = Variable.get('PIPELINE_ALPHA_LAUNCH_TIME')

dag0 = DAG('PIPELINE_ALPHA_ORDONNANCEMENT', default_args=default_args, schedule_interval=schedule)

host_project = Variable.get('HOST_PROJECT')
host_cluster = Variable.get('HOST_CLUSTER')
location = Variable.get('LOCATION')

run_sgc_sourcing = ChildDagOperator(task_id="scg_sourcing", dag_id="pipeline_alpha_sgc_sourcing", dag=dag0)
run_article_transform = ChildDagOperator(task_id="article_transform", dag_id="pipeline_alpha_article_transform", dag=dag0,
                                         retries=RETRIES)
run_contenus_sourcing = ChildDagOperator(task_id="contenus_sourcing",
                                         dag_id="contenus_sourcing", dag=dag0)
run_ra_autres_transform = ChildDagOperator(task_id="ra_autres_transform", dag_id="pipeline_alpha_ra_autres_transform",
                                           dag=dag0)
run_ref_produit_sourcing = ChildDagOperator(task_id="ref_produit_sourcing", dag_id="pipeline_alpha_ref_produit_sourcing",
                                            dag=dag0)
run_ref_produit_transform = ChildDagOperator(task_id="ref_produit_transform", dag_id="pipeline_alpha_ref_produit_transform",
                                             dag=dag0)
run_ref_produit_export = ChildDagOperator(task_id="ref_produit_export", dag_id="pipeline_alpha_ref_produit_export", dag=dag0)
run_pquadz_saphir_sourcing = ChildDagOperator(task_id="pquadz_saphir_sourcing",
                                              dag_id="pipeline_alpha_pquadz_saphir_sourcing", dag=dag0)
run_other_ref_sourcing = ChildDagOperator(task_id="other_ref_sourcing", dag_id="pipeline_alpha_other_ref_sourcing", dag=dag0)

run_fbi_sourcing = ChildDagOperator(task_id="fbi_sourcing", dag_id="pipeline_alpha_fbi_sourcing", dag=dag0)
run_fbi_transform = ChildDagOperator(task_id="fbi_transform", dag_id="pipeline_alpha_fbi_transform", dag=dag0)
run_fbi_controles_transform = ChildDagOperator(task_id="fbi_controles_transform",
                                               dag_id="pipeline_alpha_fbi_controles_transform", dag=dag0)
run_export_fbi_controles_notif = ChildDagOperator(task_id="export_fbi_controles_notif",
                                                  dag_id="pipeline_alpha_export_fbi_controles_notif", dag=dag0)

run_subsidiaries = ChildDagOperator(task_id="subsidiaries", dag_id="pipeline_alpha_subsidiaries", dag=dag0)

run_article_final_transform = ChildDagOperator(task_id="article_final_transform",
                                               dag_id="pipeline_alpha_article_final_transform", dag=dag0, retries=RETRIES)
run_article_amc = ChildDagOperator(task_id="article_amc", dag_id="pipeline_alpha_article_amc", dag=dag0, retries=RETRIES)

run_kronos_sourcing = ChildDagOperator(task_id="kronos_sourcing", dag_id="pipeline_alpha_kronos_sourcing", dag=dag0)
run_kronos_transform = ChildDagOperator(task_id="kronos_transform", dag_id="pipeline_alpha_kronos_transform", dag=dag0,
                                        retries=RETRIES)

run_agence_pub_transform = ChildDagOperator(task_id="agence_pub_transform", dag_id="pipeline_alpha_agence_pub_transform",
                                            dag=dag0)
run_ref_chutes_transform = ChildDagOperator(task_id="ref_chutes_transform", dag_id="pipeline_alpha_ref_chutes_transform",
                                            dag=dag0)
run_client_transform_last_year = ChildDagOperator(task_id="client_transform_last_year",
                                                  dag_id="pipeline_alpha_client_transform_last_year", dag=dag0,
                                                  retries=RETRIES)
run_client_transform = ChildDagOperator(task_id="client_transform", dag_id="pipeline_alpha_client_transform", dag=dag0,
                                        retries=RETRIES)

run_regional_edition = ChildDagOperator(task_id="regional_edition", dag_id="pipeline_alpha_regional_edition", dag=dag0)

run_rub_max_transform = ChildDagOperator(task_id="rub_max_transform", dag_id="pipeline_alpha_rub_max_transform", dag=dag0)
run_verticale_transform = ChildDagOperator(task_id="verticale_transform", dag_id="pipeline_alpha_verticale_transform",
                                           dag=dag0)

run_extract_preparem_nego = ChildDagOperator(task_id="extract_preparem_nego", dag_id="pipeline_alpha_extract_preparem_nego",
                                             dag=dag0)

run_commande_transform = ChildDagOperator(task_id="commande_transform", dag_id="pipeline_alpha_commande_transform", dag=dag0,
                                          trigger_rule=TriggerRule.ALL_SUCCESS)

run_produit_1_transform = ChildDagOperator(task_id="produit_1_transform", dag_id="pipeline_alpha_produit_1_transform",
                                           dag=dag0, retries=RETRIES)

run_sgc_ODIA_sourcing = ChildDagOperator(task_id="sgc_ODIA_sourcing", dag_id="pipeline_alpha_sgc_ODIA_sourcing", dag=dag0)
run_ODIA_transform = ChildDagOperator(task_id="ODIA_transform", dag_id="pipeline_alpha_ODIA_transform", dag=dag0)
run_cmdes_non_validees_transform = ChildDagOperator(task_id="cmdes_non_validees_transform",
                                                    dag_id="pipeline_alpha_cmdes_non_validees_transform", dag=dag0)
run_objectifs_tlv_sourcing = ChildDagOperator(task_id="objectifs_tlv_sourcing",
                                              dag_id="pipeline_alpha_objectifs_tlv_sourcing", dag=dag0)
run_export_objectif_tlv_transform = ChildDagOperator(task_id="objectif_tlv_export",
                                                     dag_id="pipeline_alpha_objectif_tlv_export", dag=dag0)
run_RA_2020 = ChildDagOperator(task_id="RA_2020",dag_id="RA_2020", dag=dag0)

run_ra_sourcing = ChildDagOperator(task_id="ra_sourcing", dag_id="pipeline_alpha_ra_sourcing", dag=dag0)
run_RA_transform = ChildDagOperator(task_id="RA_transform", dag_id="pipeline_alpha_RA_transform", dag=dag0)

run_export_saphir = ChildDagOperator(task_id="export_saphir", dag_id="pipeline_alpha_export_saphir", dag=dag0)

run_budget_sourcing = ChildDagOperator(task_id="budget_sourcing", dag_id="pipeline_alpha_budget_sourcing", dag=dag0)
run_budget = ChildDagOperator(task_id="budget", dag_id="pipeline_alpha_budget", dag=dag0)

run_reste_en_main_sourcing = ChildDagOperator(task_id="reste_en_main_sourcing",
                                              dag_id="pipeline_alpha_reste_en_main_sourcing", dag=dag0)
run_reste_en_main = ChildDagOperator(task_id="reste_en_main", dag_id="pipeline_alpha_reste_en_main", dag=dag0)

run_opport_affect_alim = ChildDagOperator(task_id="opport_affect_alim", dag_id="pipeline_alpha_opport_affect_alim", dag=dag0)

run_daily_backup = ChildDagOperator(task_id="daily_backup", dag_id="pipeline_alpha_daily_backup", dag=dag0,
                                    trigger_rule=TriggerRule.ALL_DONE, retries=0)

tmp_step_1 = DummyOperator(
    task_id='wait_article_step_1_all_sucess',
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag0
)

tmp_step_2 = DummyOperator(
    task_id='wait_article_step_2_all_done',
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag0
)

tmp_step_3 = DummyOperator(
    task_id='wait_article_step_3_all_done',
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag0
)

kronos_done = DummyOperator(
    task_id='wait_kronos_done',
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag0
)

run_sgc_sourcing >> run_other_ref_sourcing

run_other_ref_sourcing >> run_article_transform >> tmp_step_1
run_other_ref_sourcing >> run_pquadz_saphir_sourcing >> run_contenus_sourcing >> run_ra_autres_transform >> tmp_step_1
run_other_ref_sourcing >> run_ref_produit_sourcing >> run_ref_produit_transform
run_ref_produit_transform >> tmp_step_1
run_ref_produit_transform >> run_ref_produit_export

tmp_step_1 >> run_fbi_sourcing >> run_fbi_transform >> run_fbi_controles_transform >> run_export_fbi_controles_notif
run_fbi_controles_transform >> tmp_step_2
tmp_step_1 >> run_subsidiaries >> tmp_step_2
tmp_step_1 >> run_article_final_transform

tmp_step_2 >> run_article_final_transform >> run_article_amc

run_article_amc >> run_kronos_sourcing >> run_kronos_transform >> kronos_done >> run_rub_max_transform

run_article_amc >> run_regional_edition

run_article_amc >> run_agence_pub_transform >> run_ref_chutes_transform
run_ref_chutes_transform >> run_client_transform_last_year >> run_client_transform

run_client_transform >> run_rub_max_transform >> run_verticale_transform >> run_commande_transform

run_verticale_transform >> run_extract_preparem_nego

run_verticale_transform >> run_export_saphir
run_verticale_transform >> run_budget_sourcing >> run_budget >> tmp_step_3
run_verticale_transform >> run_reste_en_main_sourcing >> run_reste_en_main >> tmp_step_3

run_commande_transform >> run_produit_1_transform
run_commande_transform >> run_ra_sourcing >> run_RA_transform

run_sgc_sourcing >> run_RA_2020

run_sgc_sourcing >> run_sgc_ODIA_sourcing >> run_ODIA_transform >> run_cmdes_non_validees_transform
run_sgc_sourcing >> run_objectifs_tlv_sourcing

run_objectifs_tlv_sourcing >> run_export_objectif_tlv_transform
run_cmdes_non_validees_transform >> run_export_objectif_tlv_transform
run_RA_2020 >> run_export_objectif_tlv_transform

run_export_objectif_tlv_transform >> run_ra_sourcing

cube_notify = ChildDagOperator(task_id="cube_notify", dag_id="cube_notif", dag=dag0,
                               rigger_rule=TriggerRule.ALL_SUCCESS)

tmp_step_3 >> run_opport_affect_alim >> run_daily_backup
run_opport_affect_alim >> cube_notify

PIPELINE_ALPHA_DATASET = Variable.get('COMMERCIAL_DATASET')
PROJECT = Variable.get('COMMERCIAL_PROJECT')
DAILY_REPORT_EMAIL_LIST = Variable.get('DAILY_REPORT_EMAIL_LIST')
report = run_python_with_context(
    name="final_reporting",
    script=read_file("/commercial/reporting_scripts/palp_report.py"),
    env={
        'DS': "{{ds_nodash}}",
        'PROJECT': PROJECT,
        'DATASET': PIPELINE_ALPHA_DATASET,
        'DEST': DAILY_REPORT_EMAIL_LIST,
        'ENV': ENV
    },
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag0)

cube_notify >> report

report_cubes = pyrunner.run_python(
    name="cubes_reporting",
    script=read_file("/commercial/reporting_scripts/cubes_report.py"),
    env={
        'DS': "{{ds_nodash}}",
        'PROJECT': f"acme-data-dev",
        'DATASET': 'supervision_microstrategy',
        'DEST': DAILY_REPORT_EMAIL_LIST,
        'ENV': ENV,
        'MAX_TIME': '09:00'
    },
    trigger_rule=TriggerRule.ALL_DONE,
    timeout="6h",
    dag=dag0)

cube_notify >> report_cubes
