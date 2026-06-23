import hashlib
import io

from airflow.models import BaseOperator
from airflow.exceptions import AirflowException
from airflow.utils.decorators import apply_defaults
from airflow.models import Variable, DAG
import secrets
import yaml
import subprocess, os
import tempfile
import re
import signal

from pathlib import Path


class KubRunOperator(BaseOperator):
    """
      Run a pod in a job in the GKE Cluster

      This Operator assumes that the Airflow Variable KUB_PROXY_INSTANCE points to a valid kubernetes API
      The **minimum** required to define a resource to create are the variables
      ``name``,``namespace``, and ``descriptor``

      This operator supports passing files to the "/app" directory in the container either as Strings or FileReferences

      :param namespace: The K8S execution namespace
      :type namespace: str
      :param name: The task name
      :type name: str
      :param descriptor
      :type descriptor: map
      :param timeout
      :type timeout: string
      """

    @apply_defaults
    def __init__(self,
                 name,
                 descriptor,
                 namespace='composer',
                 timeout="10m",
                 verbose=False,
                 files=None,
                 krun_path=os.environ.get('DAGS_FOLDER') + "/tools/krun",
                 remote_path=None,
                 run_enrich=None,
                 *args,
                 **kwargs):
        super(KubRunOperator, self).__init__(*args, **kwargs)
        self.timeout = timeout
        self.namespace = namespace
        self.name = name
        self.descriptor = descriptor
        self.verbose = verbose
        if files:
            self.files = files
        else:
            self.files = []
        self.krun_path = krun_path
        self.remote_path = remote_path
        self.process = None
        self.run_enrich = run_enrich

    def execute(self, context):
        self._ensure_env()
        env = self.dag.get_template_env()
        if isinstance(self.descriptor, str):
            desc = yaml.safe_load(env.from_string(self.descriptor).render(**context))
        else:
            desc = self.descriptor
        files = self.files.copy()
        if self.run_enrich:
            desc, added_files = self.run_enrich(desc, context)

            files.extend(added_files)
        with tempfile.TemporaryDirectory(prefix='airflowtmp') as tmp_dir:
            if len(files) == 0:
                with open(tmp_dir + "/empty_file", 'w+') as fd:
                    fd.write("\n")
            for file in files:
                value = file['value']
                name = file['name']
                if '/' in name:
                    dirname = tmp_dir + '/' + '/'.join(name.split('/')[:-1])
                    if not os.path.exists(dirname):
                        os.makedirs(dirname)
                if isinstance(value, bytes):
                    print(f"Writing file {name}")
                    with open(tmp_dir + "/" + name, 'w+b') as fd:
                        fd.write(value)
                if isinstance(value, str):
                    print(f"Writing file {name}")
                    value = env.from_string(value).render(**context)
                    value = env.from_string(value).render(**context)
                    with open(tmp_dir + "/" + name, 'w+') as fd:
                        fd.write(value)
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as yaml_file:
                spec_yaml = yaml.safe_dump(desc, default_style='|', width=8192)
                env = self.dag.get_template_env()
                try:
                    spec_yaml = env.from_string(spec_yaml).render(**context)
                    spec_yaml = env.from_string(spec_yaml).render(**context)
                except:
                    import traceback
                    traceback.print_exc()
                    print("\n")
                    print(f"""
*************************************************************
*                     PROVIDED YAML                         *
*************************************************************
{self.descriptor}
*************************************************************
*                     TEMPLATED YAML 1                      *
*************************************************************
{desc}
*************************************************************
*                     ENRICHED YAML                         *
*************************************************************
{spec_yaml}
""")
                    raise Exception("Rendering yaml jinja template")
                yaml_file.file.write(spec_yaml)
                yaml_file.file.flush()
                self.log.info('Creating job')
                subprocess.check_output(["chmod", "a+x", self.krun_path])
                args = [self.krun_path]
                if self.remote_path:
                    args.append("-r")
                    args.append(self.remote_path)
                if self.verbose:
                    print("****************** TEMPLATED SPEC ***********************")
                    print(spec_yaml)
                    print("*********************************************************")
                    args.append("-v")

                args.extend(["-k", os.getenv("KUBECONFIG"), "-t", self.timeout, yaml_file.name,
                             tmp_dir])
                self.log.info('Calling ' + str(args))

                def pre_exec():
                    for sig in ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ'):
                        if hasattr(signal, sig):
                            signal.signal(getattr(signal, sig), signal.SIG_DFL)
                    os.setsid()

                process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT, preexec_fn=pre_exec)
                self.process = process
                self.log.info('Process started')
                line = ''
                for line in iter(process.stdout.readline, b''):
                    line = line.decode(encoding="UTF-8").rstrip()
                    self.log.info(line)
                    if line.startswith("XCom:"):
                        k, v = line[len("XCom:"):].split("=", maxsplit=1)
                        v = v.replace('"', ' ').replace("\n", "").replace("\r", "")
                        v = v.strip("'").strip()
                        self.log.info("Saving XCom: {k} -> {v}".format(k=k, v=v))
                        context['task_instance'].xcom_push(k, v)
                process.wait()
                self.log.info(
                    "Command exited with return code %s",
                    process.returncode
                )
                if process.returncode:
                    raise AirflowException(f"Job returned an error with status: {process.returncode}")
                return True

    def on_kill(self):
        self.log.info('Sending SIGTERM signal to krun process group')
        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

    def _gen_job_key(self, run_id):
        if len(run_id) > 60:
            prefix = run_id[0:45]
            h = hashlib.sha1()
            h.update(secrets.token_bytes(8))
            h.update(run_id.encode())
            postfix = h.hexdigest()[:10]
            run_id = prefix + '_' + postfix
        return re.sub("[^a-zA-Z0-9\\-]+", '-', run_id).replace('--', '-').lower().strip('-').strip()

    def _ensure_env(self):
        kubconf_str = """
            apiVersion: v1
            clusters:
            - cluster:
                insecure-skip-tls-verify: true
                server: http://KUB_PROXY_INSTANCE:8001
              name: sf_dev
            contexts:
            - context:
                cluster: "sf_dev"
              name: proxy
            current-context: "proxy"
            kind: Config
            preferences: {}
            users: []
            """.replace("KUB_PROXY_INSTANCE", Variable.get("KUB_PROXY_INSTANCE"))
        sha = hashlib.sha1()
        sha.update(kubconf_str.encode())
        h = sha.hexdigest()
        kub_config_file_name = os.path.join(tempfile.gettempdir(), h + ".kubconf")
        if not os.path.isfile(kub_config_file_name):
            with open(kub_config_file_name, 'w') as fd:
                fd.write(kubconf_str)
        os.environ["KUBECONFIG"] = kub_config_file_name
