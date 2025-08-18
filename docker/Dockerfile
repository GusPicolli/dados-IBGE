# Dockerfile
FROM apache/airflow:2.10.5-python3.9

ADD requirements.txt .
RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt

ENV RAW_PATH=${RAW_PATH}
ENV WORK_PATH=${WORK_PATH}
ENV RAW_CONFIG=${RAW_CONFIG}
ENV WORK_CONFIG=${WORK_CONFIG}
