import pandas as pd

from config.settings import DATA_DIR
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


def comments_data_load():
    logger.info("Cargando social_comments.csv (staging FactComments)")
    df = pd.read_csv(f"{DATA_DIR}/social_comments.csv")
    logger.info(f"Filas cargadas desde social_comments.csv | total={len(df)}")
    return df
