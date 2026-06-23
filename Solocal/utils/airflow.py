import hashlib
import json
import secrets
import time

import yaml

from airflow.utils.decorators import apply_defaults
from commercial.utils.kub import KubRunOperator
from airflow.models import BaseOperator, DagRun, DagBag
from airflow.exceptions import AirflowException
from commercial.utils import name2podname
from airflow import settings
from airflow import configuration as conf
import os

_dbag=None

def get_dag_execution_data(dag_run, dag):
    data = {
        'id': str(dag_run.id),
        'run_id': str(dag_run.run_id),
        'state': str(dag_run.state),
        'tasks': []
    }
    global _dbag
    if not _dbag:
        _dbag = DagBag(os.path.expanduser(conf.get('core', 'DAGS_FOLDER')))
    for task in dag_run.get_task_instances():
        task_data = {
            'task_id': str(task.task_id),
            'state': str(task.state),
            'operator': str(task.operator),
        }
        if task.execution_date:
            task_data['execution_date'] = task.execution_date.timestamp(),
        if task.start_date:
            task_data['start_date'] = task.start_date.timestamp(),
        if task.end_date:
            task_data['end_date'] = task.end_date.timestamp(),
        if task.duration:
            task_data['duration'] = task.duration
        if str(task.operator) == "ChildDagOperator" and task.state in ['failed', 'success']:
            for t in dag.tasks:
                if t.task_id == task.task_id:
                    session = settings.Session()
                    child_dag = _dbag.get_dag(t.child_dag_id)
                    candidates = [x for x in
                                  settings.Session().query(DagRun).filter(DagRun.dag_id==t.child_dag_id).filter(DagRun.run_id.like(f'{dag_run.run_id}%'))]
                    if len(candidates) == 0:
                        raise AirflowException(
                            f"Could not find dag run for task {t.task_id} with run_id {dag_run.run_id}")
                    elif len(candidates) > 1:
                        child_dag_run = sorted(candidates, key=lambda dr: dr.start_date, reverse=True)[0]
                    else:
                        child_dag_run = candidates[0]
                    session.close()
                    task_data["child_dag"] = get_dag_execution_data(child_dag_run, child_dag)
        data['tasks'].append(task_data)
    return data


class KubRunWithAirflowContextOperator(KubRunOperator):

    @apply_defaults
    def __init__(self,
                 *args,
                 **kwargs):
        super(KubRunWithAirflowContextOperator, self).__init__(*args, **kwargs)

    def execute(self, context):
        data = get_dag_execution_data(context['dag_run'], context['dag'])
        file = {'name': 'dagrun.json', 'value': json.dumps(data)}
        self.files.append(file)
        KubRunOperator.execute(self, context)


class ChildDagOperator(BaseOperator):

    @apply_defaults
    def __init__(self, dag_id, *args, **kwargs):
        super(ChildDagOperator, self).__init__(*args, **kwargs)

        self.child_dag_id = dag_id

    def execute(self, context):
        h = hashlib.sha1()
        h.update(secrets.token_bytes(8))
        postfix = h.hexdigest()[:8]
        run_id = "{}_{}_{}".format(context["dag_run"].run_id, self.child_dag_id, postfix)
        from airflow.api.common.experimental.trigger_dag import trigger_dag
        from random import randrange
        dagrun = trigger_dag(self.child_dag_id, run_id=run_id,
                             execution_date=context["execution_date"].replace(microsecond=randrange(999999)),
                             replace_microseconds=False)
        while True:
            state = dagrun.update_state()
            self.log.info("Child dag: " + state)
            from airflow.utils.state import State
            if state in [State.FAILED, State.UPSTREAM_FAILED, State.SKIPPED]:
                raise AirflowException("Child dag failed with status: {0}".format(state))
            elif state in [State.SUCCESS]:
                return True
            time.sleep(10)


def run_python_with_context(name, script, files=None, env=None, **kwargs):
    if not files:
        files = []
    if "memory" in kwargs:
        mem = int(kwargs["memory"])
    else:
        mem = 512
    podname = name2podname(name)
    desc = f"""
kind: Pod
apiVersion: v1
metadata:
  name: '{podname}'
  namespace: composer
spec:
  containers:
    - name: krun-test1
      image: registry.gitdata.example.com/data/transverse/docker-images/python-gcloud:latest
      resources:
        requests:
          memory: {mem}Mi
          cpu: .25
        limits:
          memory: {mem}Mi
          cpu: 1
      args:
        - /usr/local/bin/python3
        - /app/script.py
      env:
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /var/secrets/google/bigquery-key.json
      volumeMounts:
        - name: google-cloud-key
          mountPath: /var/secrets/google
          readOnly: true
        - name: rclone
          mountPath: /var/secrets/rclone
          readOnly: true
        - name: sendgrid
          mountPath: /var/secrets/sendgrid
          readOnly: true
  restartPolicy: Never
  imagePullSecrets:
    - name: gitlab-key
  volumes:
    - name: google-cloud-key
      secret:
        secretName: bigquery-key
    - name: rclone
      secret:
        secretName: rclone
    - name: sendgrid
      secret:
        secretName: sendgrid
    """
    f = files.copy()
    f.append({"name": "script.py", "value": script})
    desc = yaml.load(desc)
    if env:
        env2 = desc["spec"]["containers"][0]["env"]
        for e in env:
            env2.append({"name": e, "value": env[e]})
        desc["spec"]["containers"][0]["env"] = env2
    return KubRunWithAirflowContextOperator(name=name, task_id=name, descriptor=desc,
                                            files=f, **kwargs)
