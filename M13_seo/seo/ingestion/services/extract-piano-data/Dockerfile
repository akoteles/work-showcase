FROM python:3.8-slim

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY run.sh /

RUN apt-get update  \
&& apt-get install -y --no-install-recommends ca-certificates cron  \
&& chmod +x /run.sh

COPY files/api.py files/config.py files/helpers.py files/main.py files/bigquery.py /

CMD ["/run.sh"]
