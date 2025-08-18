from airflow import DAG
import json
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator
from datetime import datetime, timedelta

ingestion_lambda_function_name = "coingecko_etl_ingestao"
preparation_lambda_function_name = "coingecko_etl_preparacao"

with DAG(
    "coinGecko_coins_api",
    start_date=datetime(2023, 10, 10), 
    schedule_interval=timedelta(minutes=60),
    catchup=False
) as dag:

    t0 = LambdaInvokeFunctionOperator(
        task_id='ingestion_task',
        function_name=ingestion_lambda_function_name,
        payload=json.dumps({"subsource": "coingecko"}),
        aws_conn_id='aws_default'
    )


    t1 = LambdaInvokeFunctionOperator(
        task_id='preparation_task',
        function_name=preparation_lambda_function_name,
        payload="{{ task_instance.xcom_pull(task_ids='ingestion_task') }}",
        aws_conn_id='aws_default'
    )

    t0 >> t1