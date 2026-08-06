import pandas as pd

from config.settings import DATA_DIR
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


def opiniones_data_load():
    logger.info("Cargando surveys_part1.csv (staging FactOpiniones)")
    df = pd.read_csv(f"{DATA_DIR}/surveys_part1.csv")
    logger.info(f"Filas cargadas desde surveys_part1.csv | total={len(df)}")
    return df
