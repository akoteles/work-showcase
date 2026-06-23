import logging

from airflow import AirflowException
from airflow.models import TaskInstance, SkipMixin, BaseOperator
from airflow.utils.db import provide_session
from airflow.utils.state import State


class FinalStateOperator(BaseOperator, SkipMixin):
    def __init__(
            self,
            run_once_task_id=None,
            skip_task_id=None,
            *args, **kwargs):
        super(FinalStateOperator, self).__init__(*args, **kwargs)

        self.run_once_task_id = run_once_task_id
        self.skip_task_id = skip_task_id

    @provide_session
    def execute(self, context, session=None):
        print("execute FinalStateOperator operator")
        logging.info("execute FinalStateOperator operator")

        TI = TaskInstance
        ti = session.query(TI).filter(
            TI.dag_id == context['dag'].dag_id,
            TI.task_id.in_([t for t in self.upstream_task_ids]),
            TI.execution_date == context['task_instance'].execution_date
        ).all()

        previous_failed = [t for t in ti if t.state == State.FAILED or t.state == State.UPSTREAM_FAILED]

        if previous_failed:
            logging.info('Found existing task run (%s) with state Failed or UPSTREAM_FAILED. ', previous_failed)

            raise AirflowException('Fail caused by a failing task %s' % previous_failed)
        else:
            logging.info('Found no existing task run with state fail. '
                         'Therefore run the direct downstream task')

        logging.info("Done.")
