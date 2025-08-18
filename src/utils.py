import requests
import json
import sys
import os
import pandas as pd
import awswrangler as wr
from aws_lambda_powertools import Logger
import env as env
from functools import partial
logger = Logger(log_record_order=["level", "message", "location"])
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)


def request_data(url: str, params:dict) -> dict:
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
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Erro ao fazer a requisição: {e}")
        raise
    except json.JSONDecodeError:
        logger.error("Erro ao decodificar a resposta JSON.")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        raise

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
        path_file = f"{path}/{filename}.parquet"
        logger.info(path_file)
        wr.s3.to_parquet(
            df = df_,
            path=path_file
        )
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
    """   No
    Handles the ingestion process: requests data from a URL and saves it as a Parquet file.
        
        Args:
            event (dict): A dictionary with the event parameters, including the "subsource".
    """
    #path_config = env.RAW_CONFIG
    config_path = os.path.join(BASE_DIR, "assets", "config.ingestion.json")
    with open(config_path, 'r') as json_data:
        config_ingestion = json.load(json_data)
    data = request_data(
        config_ingestion["url"],
        params=config_ingestion["parameters"]
    )
    results_path = data[0][config_ingestion['results_field']]
    df = pd.DataFrame(results_path)
    df = get_steps(df, pre_steps=[explode_column, normalize], post_steps=[])
    path_raw = env.RAW_PATH
    payload["path_file"] = load_data(
        df,
        path_raw, 
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
    path_config = env.WORK_CONFIG
    metadado = json.load(open(path_config))
    path_raw = payload["path_raw"]
    df = wr.s3.read_parquet(
        path_raw
    )

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
    
    path_work = env.WORK_PATH
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

def normalize(df:pd.DataFrame, columns:list):
    df_concat = pd.DataFrame
    for column in columns:
        df_column = pd.json_normalize(df[column]).set_index(df.index)
        df_concat = pd.concat([df_concat, df_column], axis=1)
    return df_concat
