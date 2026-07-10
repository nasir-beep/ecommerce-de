FROM apache/airflow:2.8.0-python3.11

WORKDIR /opt/airflow

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY airflow/dags /opt/airflow/dags
COPY scripts /opt/airflow/scripts

ENV AIRFLOW_HOME=/opt/airflow
