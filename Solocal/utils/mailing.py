from commercial.utils import pyrunner, read_script

_smail_send_script = read_script('simple_mail_send.py')
_attachement_send_script = read_script('att_mail_send.py')
_sql_send_script = read_script('sql_mail_send.py')


def send_mail(name, subject, recipients, contents, **kwargs):
    env = {
        'TO': ','.join(recipients),
        'SUBJECT': subject,
        'CONTENTS': contents,
    }
    return pyrunner.run_python(name, script=_smail_send_script, env=env, **kwargs)


def send_attachement(name, subject, recipients, contents, bucket, paths, **kwargs):
    env = {
        'TO': ','.join(recipients),
        'SUBJECT': subject,
        'CONTENTS': contents,
        'BUCKET': bucket,
        'PATHS': ','.join(paths)
    }
    return pyrunner.run_python(name, script=_attachement_send_script, env=env, **kwargs)


def send_simple_sql(name, subject, recipients, contents, sql, **kwargs):
    env = {
        'TO': ','.join(recipients),
        'SUBJECT': subject,
    }
    return pyrunner.run_python(name,
                               script=_sql_send_script,
                               files=[
                                   {'name': 'query.sql', 'value': sql},
                                   {"name": "mail.md", "value": contents}
                               ],
                               env=env, **kwargs)


def mailing_alert_component(dag, prev_task, next_task, op=None):
    from airflow.models import Variable
    from airflow.operators.dummy_operator import DummyOperator
    from airflow.utils.trigger_rule import TriggerRule

    def set_mailing_alert(task_id,
                          subject,
                          contents,
                          dag,
                          prd_dest=["alerts-prod@example.com"],
                          rec_dest=["alerts-rec@example.com"],
                          trigger_rule=TriggerRule.ALL_SUCCESS):

        ENV = Variable.get('ENV')

        if ENV.upper() == "PRD":
            send = send_mail(name=task_id,
                             subject=f"[{ENV}] {subject}",
                             recipients=prd_dest,
                             contents=contents,
                             dag=dag,
                             trigger_rule=trigger_rule)
        elif ENV.upper() == "REC":
            send = send_mail(name=task_id,
                             subject=f"[{ENV}] {subject}",
                             recipients=rec_dest,
                             contents=contents,
                             dag=dag,
                             trigger_rule=trigger_rule)
        else:
            send = DummyOperator(task_id=task_id, dag=dag, trigger_rule=trigger_rule)

        return send

    mail_done = DummyOperator(
        task_id='mail_sent',
        trigger_rule=TriggerRule.ALL_DONE,
        dag=dag
    )

    id = op if op else dag.dag_id
    mailing_alert_ok = set_mailing_alert(task_id="send_mail_ok",
                                         subject=f"[PALP] {id} OK",
                                         contents="%s Succeeded for run {{ds}}" % id,
                                         dag=dag)

    mailing_alert_Nok = set_mailing_alert(task_id="send_mail_Nok",
                                          subject=f"[PALP] {id} FAILED",
                                          contents="%s Failed for run {{ds}}" % id,
                                          trigger_rule=TriggerRule.ONE_FAILED,
                                          dag=dag)

    mailing_alert_Nok >> mail_done
    mailing_alert_ok >> mail_done

    prev_task >> mailing_alert_Nok
    prev_task >> mailing_alert_ok

    mail_done >> next_task
    return
