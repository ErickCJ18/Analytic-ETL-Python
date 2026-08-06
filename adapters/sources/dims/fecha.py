import pandas as pd

from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)

START_DATE = '2024-09-13'
END_DATE = '2025-09-14'


def fecha_data_load():
    logger.info(f"Generando calendario DimFecha | rango={START_DATE} a {END_DATE}")
    fechas = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
    df_fecha = pd.DataFrame({'FullDate': fechas})
    logger.info(f"Calendario generado | total_fechas={len(df_fecha)}")
    return df_fecha
