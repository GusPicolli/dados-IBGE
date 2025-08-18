import datetime as dt
from utils import (ingestion, preparation)
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
logger = Logger(log_record_order=["level", "message", "location"])


def ingestion_handler(event: dict, context=LambdaContext) -> dict:
    """
    Handles data ingestion.

    Logs the start and end times, and calls the 'ingestion' function from 'utils'.
    
    Args:
        event (dict): A dictionary with the parameters for ingestion. Example:
            {
                "subsource": "coingecko"
            }
    
    Returns:
        dict: The result from the 'ingestion' function.
    """
    payload = event
    logger.info("Início da ingestão: %s", str(dt.datetime.now()))
    payload["path_raw"] = ingestion(event)
    logger.info("Fim da ingestão: %s", str(dt.datetime.now()))
    logger.info("Payload gerado: %s", str(payload))
    return payload


def preparation_handler(event: dict, context=LambdaContext) -> dict:
    """
    Handles data preparation.

    Logs the start and end times, and calls the 'preparation' function from 'utils'.
    
    Args:
        event (dict): A dictionary with the parameters for preparation. Example:
            {
                "subsource": "coingecko"
            }
    
    Returns:
        dict: The result from the 'preparation' function.
    """
    payload = event
    logger.info("Início da preparação: %s", str(dt.datetime.now()))
    payload["path_work"] = preparation(event)
    logger.info("Fim da preparação: %s", str(dt.datetime.now()))
    logger.info("Payload gerado: %s", str(payload))
    return payload


if __name__ == "__main__":
    ingestion_handler({
        "subsource": "coingecko"
    })
    #preparation_handler({
    #    "subsource": "coingecko"
    #})
