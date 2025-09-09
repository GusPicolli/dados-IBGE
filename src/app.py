import datetime as dt
import env
from utils import (ingestion, preparation)
import logging
#from aws_lambda_powertools.utilities.typing import LambdaContext
logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


def bronze_handler(event: dict) -> dict:
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


def silver_handler(event: dict) -> dict:
    """
    Handles data preparation.

    Logs the start and end times, and calls the 'preparation' function from 'utils'.
    
    Args:
        event (dict): A dictionary with the parameters for preparation. Example:
            {
                "subsource": "internet"
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
    bronze_handler({
        "subsource": "internet"
    })
    silver_handler({
        "subsource": "internet",
        "path_raw": f"{env.BRONZE_PATH}/internet.parquet"
    })
#