import requests
from requests.adapters import HTTPAdapter, Retry
import json
import time
import sys
import os
import pandas as pd
#import awswrangler as wr
#from aws_lambda_powertools import Logger
import env as env
import logging
from functools import partial
logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

#BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
#sys.path.append(BASE_DIR)


def request_data(config_dict: dict, retries = 3,  backoff_factor=2) -> dict:
    """
    Sends a GET request to the specified URL with given parameters, returns the response as a dictionary.
        
        Args:
            url (str): The URL to send the request to.
            params (dict): The parameters to include in the r
            equest.
        
        Returns:
            dict: JSON response from the API.

        Raises:
            RequestException: If there's an issue with the HTTP request.
            JSONDecodeError: If the response cannot be parsed as JSON.
            Exception: For any unexpected errors.
    """
    for attempt in range(retries):
        try:
            response = requests.get(config_dict["url"], params=config_dict["parameters"], timeout=10)
            response.raise_for_status()
            results = response.json()
            if 'results_field' in config_dict:
                data = results[0][config_dict['results_field']]
            return data
        except (requests.exceptions.RequestException, ValueError) as e:
                wait_time = backoff_factor ** attempt
                print(f"Tentativa {attempt+1} falhou: {e}. Retentando em {wait_time}s...")
                time.sleep(wait_time)
    raise Exception("Falha após várias tentativas.")

def load_data(df_:pd.DataFrame, path: str, filename: str) -> str:
    """
    Saves the DataFrame as a Parquet file to the specified path.
        
        Args:
            df (pd.DataFrame): The data to be saved.
            path (str): Directory to save the file.
            filename (str): Name of the file.
        
        Returns:
            str: Path where the file was saved.

        Raises:
            KeyError: If a key is not found in the DataFrame.
            ValueError: If the data cannot be converted to a DataFrame.
            Exception: For any unexpected errors.
    """
    try:
        # garante que o diretório existe
        os.makedirs(path, exist_ok=True)

        path_file = f"{path}/{filename}.parquet"
        logger.info(path_file)

        df_.to_parquet(path_file, index=False)

        logger.info(f"Arquivo salvo em {path}")

        return path_file
    except KeyError as e:
        logger.error(f"Chave não encontrada no DataFrame: {e}")
        raise
    except ValueError as e:
        logger.error(f"Erro ao converter os dados para DataFrame: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao salvar o arquivo: {e}")
        raise

def ingestion(payload: dict):
    """   
    Handles the ingestion process: requests data from a URL and saves it as a Parquet file.
        
        Args:
            event (dict): A dictionary with the event parameters, including the "subsource".
    """
    print(env.BASE_DIR)
    config_path = os.path.join(env.BASE_DIR, "assets", f"bronze.{payload['subsource']}.json")

    with open(config_path, 'r') as json_data:
        config_dict = json.load(json_data)
    
    data = request_data(
        config_dict
    )
    df = pd.DataFrame(data)
   
    payload["path_file"] = load_data(
        df,
        env.BRONZE_PATH,
        payload["subsource"]
    )
    return payload

def preparation(payload: dict):
    """
    Handles the preparation process: reads a Parquet file, transforms data types according to metadata, 
        and saves the processed data.
        
        Args:
            event (dict): A dictionary with the event parameters, including the "subsource".
    """

    path_config = os.path.join(env.BASE_DIR, "assets", f"silver.{payload['subsource']}.json")
    metadado = json.load(open(path_config))
    path_raw = payload["path_raw"]

    df = pd.read_parquet(
        path_raw
    )
    df = get_steps(df, pre_steps=[
        explode_column,
        normalize_columns
    ], post_steps=[])

    for coluna in metadado:
        try:
            if metadado[coluna] == 'string':
                df[coluna] = df[coluna].astype(str)
            if metadado[coluna] == 'double':
                df[coluna] = df[coluna].astype(float)
            if metadado[coluna] == 'timestamp':
                df[coluna] = pd.to_datetime(df[coluna]).dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            raise (f"Erro inesperado ao fazer a tratamento dos dados:{e}")
    
    path_work = env.SILVER_PATH
    payload["path_file"] = load_data(
        df, 
        path_work, 
        payload["subsource"]
    )
    return payload

def get_steps(df:pd.DataFrame, pre_steps:list, post_steps:list):
    """
    Handles the preparation process: reads a Parquet file, transforms data types according to metadata, 
        and saves the processed data.
        
        Args:
            event (dict): A dictionary with the event parameters, including the "subsource".
    """
    for step in pre_steps:
        df = step(df, columns=['classificacoes','series'])
    return df


def explode_column(df:pd.DataFrame, columns:list):
    for column in columns:
        df = df.explode(column)
    return df

def normalize_columns(df:pd.DataFrame, columns:list):
    df_concat = pd.DataFrame()
    for column in columns:
        df_column = pd.json_normalize(df[column])
        df_concat = pd.concat([df_concat, df_column], axis=1)
    return df_concat
