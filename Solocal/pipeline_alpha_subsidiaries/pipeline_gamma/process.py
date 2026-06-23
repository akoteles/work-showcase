import os
from google.cloud import bigquery
from google.cloud import storage
from google.cloud.bigquery import WriteDisposition
import io
from string import Template
import requests
import xml.etree.ElementTree as ET
from  datetime import datetime
import csv

project = os.getenv("PROJECT")
dataset = os.getenv("DATASET")
bucket = os.getenv("BUCKET")
path = os.getenv("PATH")

bq = bigquery.Client(project=project)

gcs = storage.Client(project=project)

select_epj = Template('''
  SELECT
    NO_EPJ, DA_EPJ
  FROM ( /* Recherche sur la vraie date de rem */
    SELECT
      lpad(TV.NO_ETAB,
        8,
        '0') AS NO_EPJ,
      FORMAT_DATE('%d/%m/%Y', (CASE UPPER(TV.LI_ORIGINE_VENTE)
            WHEN 'FACTURATION' THEN TV.DA_FACTURATION
            ELSE TV.DA_SOUSCR END)) AS DA_EPJ
    FROM
      `${project}.${dataset}.TWH_STA_PALP_SALES_TRANSACTIONS_SUBSIDIARIES` TV
    INNER JOIN (
      SELECT
        NO_EPJ
      FROM
        `${project}.${dataset}.TWH_ODS_PALP_REF_CONTACTS_EPJ_HISTO`
      GROUP BY
        NO_EPJ ) TC
    ON
      CAST(TV.NO_ETAB AS INT64) = TC.NO_EPJ
      AND CAST(TV.NO_FLAG_DELETED as int64) <> 1
    WHERE
      CAST(TV.NO_FLAG_DELETED as int64) <> 1
      AND (CASE
          WHEN CAST( ${noflagdeleted} AS int64) = 0 THEN 1
          ELSE 0 END) = 1
    UNION DISTINCT
      /* Recherche sur la date de rem + 7 jours */
    SELECT
      lpad(CAST(NO_ETAB AS STRING),
        8,
        '0') AS NO_EPJ,
      FORMAT_DATE('%d/%m/%Y', DATE_ADD(DA_EVENT, INTERVAL 7 DAY)) AS DA_EPJ
    FROM
      `${project}.${dataset}.TWH_STA_PALP_REF_REFERENT_EPJ`
    WHERE
      CO_SOURCE = 'SUBSIDIARIES'
      AND (NO_ETAB_WS IS NULL
        OR IFNULL(TRIM(NO_COML),
          '') = '')
      AND (CASE
          WHEN CAST( ${noflagdeleted} AS int64) = 0 THEN 0
          ELSE 1 END) = 1
    GROUP BY
      NO_EPJ,
      DA_EPJ
    UNION DISTINCT
      /* Recherche du référent pour la deuxième sales_transactions 24mois filiale */
    SELECT
      DISTINCT lpad(CAST(no_etab AS STRING),
        8,
        '0') AS NO_EPJ,
      FORMAT_DATE('%d/%m/%Y', (CASE
            WHEN CAST(da_valid_vente as DATE)>current_date AND EXTRACT(hour  FROM  current_timestamp)>=22 THEN current_date
            WHEN CAST(da_valid_vente as DATE)>current_date
          AND EXTRACT(hour
          FROM
            current_timestamp)<22 THEN DATE_SUB(current_date, INTERVAL 1 DAY)
            ELSE CAST(da_valid_vente as DATE) END)) AS DA_EPJ
    FROM
      `${project}.${dataset}.TWH_ODS_PALP_SALES_TRANSACTIONS_SUBSIDIARIES`
    WHERE
      co_filiale = 'PJMS'
      AND CAST(da_valid_vente as DATE) BETWEEN DATE_SUB(current_date, INTERVAL 1 DAY)
      AND DATE_ADD(current_date, INTERVAL 90 DAY)
      AND duree_engagement = 24
      AND DATE_DIFF(CAST(da_valid_vente as DATE),
        CAST(da_souscr as DATE),
        MONTH) > 10 ) T1
''')


def do_ws_call(noflagdeleted):
    sql = select_epj.substitute({
        'project': project,
        'dataset': dataset,
        'noflagdeleted': noflagdeleted
    })
    epjs = [x for x in bq.query(query=sql).result()]

    reqHead = '''\
    <soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' xmlns:web='http://webservices.pipeline_gamma.pj.fr/'>
        <soapenv:Header/>
        <soapenv:Body>
            <web:getListeReferentADate>
    '''

    reqFoot = '''\
            </web:getListeReferentADate>
        </soapenv:Body>
    </soapenv:Envelope>
    '''

    lines = [reqHead]
    for row in epjs:
        lines.append("\t\t<EPJetDate><EPJ>" + row['NO_EPJ'] + "</EPJ><date>" + row['DA_EPJ'] + "</date></EPJetDate>\n")

    lines.append(reqFoot)
    req = ''.join(lines)

    headers = {
        'SOAPAction': '',
        'Content-Type': 'application/xml'
    }
    res = requests.post("http://pipeline_gamma.pj.fr/PipelineGammaServer/services/WSConsultation", headers=headers, data=req)
    if not res.ok:
        raise Exception(f"Error from PIPELINE_GAMMA Web Service Call:{res.text}")
    tree = ET.fromstring(res.text)
    output = []
    for i, epj in enumerate(epjs):
        output_row = {
            'NO_FLAG_DELETED': noflagdeleted,
            'NO_ETAB': epj['NO_EPJ'],
            'DA_EVENT': datetime.strptime(epj['DA_EPJ'],'%d/%m/%Y').strftime('%Y-%m-%d'),
            'CO_SOURCE': 'SUBSIDIARIES',
        }
        r = {}
        for col in tree[0][0][i]:
            r[col.tag] = col.text
        output_row['AN_PARUT'] = r.get('anParut', '')
        output_row['CO_BU'] = r.get('bu', '')
        output_row['CO_BU_REGION'] = r.get('buRegion', '')
        output_row['CO_EQP_VENTE'] = r.get('equipe', '')
        output_row['CO_FORCE_VENTE'] = r.get('forceDeVente', '')
        output_row['CO_GRP_VENTE'] = r.get('groupe', '')
        output_row['CO_CANAL'] = r.get('canal', '')
        output_row['NO_COML'] = r.get('commercial', '')
        output_row['NO_ETAB_WS'] = r.get('noCli', '')
        output_row['NO_LOT_AFFECT'] = r.get('noLotAffect', '')
        output_row['NO_LOT_EDI'] = r.get('noLotEdi', '')
        output_row['CO_RAISON_TRANSFERT'] = r.get('raisonTransfert', '')
        output_row['CO_SEGMENT'] = r.get('segment', '')
        output.append(output_row)
    return output


def write_output_csv(data):
    buffer = io.StringIO()
    fieldnames = [
        'NO_FLAG_DELETED',
        'NO_ETAB',
        'DA_EVENT',
        'CO_SOURCE',
        'AN_PARUT',
        'CO_BU',
        'CO_BU_REGION',
        'CO_CANAL',
        'NO_COML',
        'CO_EQP_VENTE',
        'CO_FORCE_VENTE',
        'CO_GRP_VENTE',
        'NO_ETAB_WS',
        'NO_LOT_AFFECT',
        'NO_LOT_EDI',
        'CO_RAISON_TRANSFERT',
        'CO_SEGMENT',
    ]
    writer = csv.writer(buffer)
    writer.writerow(fieldnames)
    for row in data:
        writer.writerow(
            [
                row.get('NO_FLAG_DELETED', ''),
                row.get('NO_ETAB', ''),
                row.get('DA_EVENT', ''),
                row.get('CO_SOURCE', ''),
                row.get('AN_PARUT', ''),
                row.get('CO_BU', ''),
                row.get('CO_BU_REGION', ''),
                row.get('CO_CANAL', ''),
                row.get('NO_COML', ''),
                row.get('CO_EQP_VENTE', ''),
                row.get('CO_GRP_VENTE', ''),
                row.get('CO_FORCE_VENTE', ''),
                row.get('NO_ETAB_WS', ''),
                row.get('NO_LOT_AFFECT', ''),
                row.get('NO_LOT_EDI', ''),
                row.get('CO_RAISON_TRANSFERT', ''),
                row.get('CO_SEGMENT', ''),
            ]
        )
    return buffer.getvalue()


def insert_csv_into_bq(data, file_name):
    blob = gcs.bucket(bucket).blob(path + "/" + file_name + ".csv")
    blob.upload_from_string(data)

    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.write_disposition = WriteDisposition.WRITE_APPEND
    job_config.skip_leading_rows = 1
    job_config.allow_quoted_newlines = True
    load_job = bq.load_table_from_uri(f'gs://{bucket}/{path}/{file_name}.csv',
                                      f'{project}.{dataset}.TWH_STA_PALP_REF_REFERENT_EPJ',
                                      job_config=job_config)
    try:
        load_job.result()
    except:
        for err in load_job.errors:
            print(f"ERROR:{err}")
        raise Exception("Inserting data")
    return load_job.output_rows


def iteration(name, no_flag_deleted):
    print(f"Iteration {name}")
    print("Web service call")
    update = do_ws_call(no_flag_deleted)
    print("Create CSV")
    csv = write_output_csv(update)

    purge = f'''
        delete from `{project}.{dataset}.TWH_STA_PALP_REF_REFERENT_EPJ`
            where upper(CO_SOURCE) = 'SUBSIDIARIES'
            and CAST(NO_FLAG_DELETED as int64) = {no_flag_deleted}
    '''
    print("Purge table")
    purge_job = bq.query(purge)
    purge_job.result()
    print(f"Purged {purge_job.num_dml_affected_rows} rows")
    print("Inserting updated data")
    inserted_rows = insert_csv_into_bq(csv, name)
    print(f"Inserted {inserted_rows} rows")


iterations = [
    (0, 'iteration_1'),
    (-1, 'iteration_2')
]

for iter in iterations:
    iteration(iter[1], iter[0])
