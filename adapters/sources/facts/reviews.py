import pandas as pd

from config.settings import DATA_DIR
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


def reviews_data_load():
    logger.info("Cargando web_reviews.csv (staging FactReviews)")
    df = pd.read_csv(f"{DATA_DIR}/web_reviews.csv")
    logger.info(f"Filas cargadas desde web_reviews.csv | total={len(df)}")
    return df
