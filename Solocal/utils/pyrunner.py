from commercial.utils import name2podname
from commercial.utils.kub import KubRunOperator
from airflow.utils.decorators import apply_defaults
import yaml


def run_python(name, script, files=None, env=None, **kwargs):
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
    return KubRunOperator(name=name, task_id=name, descriptor=desc,
                          files=f, **kwargs)
