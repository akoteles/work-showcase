from commercial.utils import pyrunner, read_script, name2podname
from commercial.utils.kub import KubRunOperator
from airflow.models import Variable
import yaml

_load_avro_script = read_script('load_avro.py')
_load_transform_script = read_script('load_transform.py')


def load_transform(
        name,
        urls,
        table,
        project=Variable.get('COMMERCIAL_PROJECT'),
        dataset=Variable.get('COMMERCIAL_DATASET'),
        tmp_dataset=Variable.get('COMMERCIAL_DATASET_TMP'),
        format="AVRO",
        separator=',',
        has_header=True,
        schema=None,
        transform_sql=None,
        overwrite=True,
        **kwargs):
    env = {
        'URL': ",".join(urls),
        'PROJECT': project,
        'DATASET': dataset,
        'TABLE': table,
        'TMP_DATASET': tmp_dataset,
        'FORMAT': format,
        'SEPARATOR': separator,
        'HAS_HEADER': has_header,
        'JAGGED_ROWS': kwargs.get('allow_jagged_rows', False),
        'TRUNCATE': str(overwrite),
        'QUOTED_LF': kwargs.get('allow_quoted_newlines', False)

    }
    files = []
    if schema:
        files.append({'name': 'schema.json', 'value': schema})
    if transform_sql:
        files.append({'name': 'transform.sql', 'value': transform_sql})
    return pyrunner.run_python(name, script=_load_transform_script, env=env, files=files, **kwargs)


def load_avro(name, bucket, path, table, project=Variable.get('COMMERCIAL_PROJECT'),
              dataset=Variable.get('COMMERCIAL_DATASET'), overwrite=True, partition=None, partition_expiry=None,
              **kwargs):
    env = {
        'BUCKET': bucket,
        'PATH': path,
        'DATASET': dataset,
        'TABLE': table,
        'TRUNCATE': str(overwrite),
        'PROJECT': project,
    }
    if partition:
        env["PARTITION_BY"] = partition
    if partition_expiry:
        env["PARTITION_EXPIRY"] = partition_expiry
    return pyrunner.run_python(name, script=_load_avro_script, env=env, **kwargs)


def source_sql(name,
               jdbc_url,
               user,
               password,
               sql,
               bucket,
               path,
               prefetch=None,
               limit=None,
               input_encoding=None,
               output_encoding=None,
               type_overrides=None,
               **kwargs):
    podname = name2podname(name)
    dest = f"gs://{bucket}/{path}.avro"
    desc = f"""
kind: Pod
apiVersion: v1
metadata:
  name: '{podname}'
  namespace: composer
spec:
  containers:
    - name: puller
      image: registry.gitdata.example.com/data/transverse/docker-images/sql-puller:latest
      imagePullPolicy: Always
      resources:
        requests:
          memory: "1Gi"
          cpu: "1"
        limits:
          memory: "1Gi"
          cpu: "2"
      args: ["-v",
             "sql",
             "-d", "{dest}",
             "-J" ,"{jdbc_url}",
             "-u", "{user}",
             "-p", "{password}"]
      env:
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /var/secrets/google/bigquery-key.json
      volumeMounts:
        - name: google-cloud-key
          mountPath: /var/secrets/google
          readOnly: true
  restartPolicy: Never
  imagePullSecrets:
    - name: gitlab-key
  volumes:
    - name: google-cloud-key
      secret:
        secretName: bigquery-key
    """
    desc2 = yaml.load(desc)
    if prefetch:
        desc2["spec"]["containers"][0]["args"].append("--prefetch")
        desc2["spec"]["containers"][0]["args"].append(str(prefetch))
    if limit:
        desc2["spec"]["containers"][0]["args"].append("--limit")
        desc2["spec"]["containers"][0]["args"].append(str(limit))
    if input_encoding and output_encoding:
        desc2["spec"]["containers"][0]["args"].append("--force_transcode")
        desc2["spec"]["containers"][0]["args"].append(f"{input_encoding},{output_encoding}")
    if type_overrides:
        for t in type_overrides:
            column, new_type, nullable = t[0], t[1], t[2]
            desc2["spec"]["containers"][0]["args"].append("--type")
            desc2["spec"]["containers"][0]["args"].append(f"{column},{new_type},{nullable}")
    desc2["spec"]["containers"][0]["args"].append(sql)
    return KubRunOperator(name=name, task_id=name, descriptor=desc2,
                          files=[], remote_path='/data', **kwargs)


def source_table(name,
                 jdbc_url,
                 user,
                 password,
                 table,
                 bucket,
                 path,
                 prefetch=None,
                 limit=None,
                 input_encoding=None,
                 output_encoding=None,
                 type_overrides=None,
                 **kwargs):
    podname = name2podname(name)
    dest = f"gs://{bucket}/{path}.avro"
    desc = f"""
kind: Pod
apiVersion: v1
metadata:
  name: {podname}
  namespace: composer
spec:
  containers:
    - name: puller
      image: registry.gitdata.example.com/data/transverse/docker-images/sql-puller:latest
      imagePullPolicy: Always
      resources:
        requests:
          memory: "1Gi"
          cpu: "1"
        limits:
          memory: "1Gi"
          cpu: "2"
      args: ["-v",
             "sqltable",
             "-d", "{dest}",
             "-J" ,"{jdbc_url}",
             "-u", "{user}",
             "-p", "{password}",
      ]
      env:
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /var/secrets/google/bigquery-key.json
      volumeMounts:
        - name: google-cloud-key
          mountPath: /var/secrets/google
          readOnly: true
  restartPolicy: Never
  imagePullSecrets:
    - name: gitlab-key
  volumes:
    - name: google-cloud-key
      secret:
        secretName: bigquery-key
    """
    desc2 = yaml.load(desc)
    if prefetch:
        desc2["spec"]["containers"][0]["args"].append("--prefetch")
        desc2["spec"]["containers"][0]["args"].append(str(prefetch))
    if limit:
        desc2["spec"]["containers"][0]["args"].append("--limit")
        desc2["spec"]["containers"][0]["args"].append(str(limit))
    if input_encoding and output_encoding:
        desc2["spec"]["containers"][0]["args"].append("--force_transcode")
        desc2["spec"]["containers"][0]["args"].append(f"{input_encoding},{output_encoding}")
    if type_overrides:
        for t in type_overrides:
            column, new_type, nullable = t[0], t[1], t[2]
            desc2["spec"]["containers"][0]["args"].append("--type")
            desc2["spec"]["containers"][0]["args"].append(f"{column},{new_type},{nullable}")
    desc2["spec"]["containers"][0]["args"].append(table)
    return KubRunOperator(name=name, task_id=name, descriptor=desc2,
                          files=[], remote_path='/data', **kwargs)
