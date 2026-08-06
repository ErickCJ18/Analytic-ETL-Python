import pandas as pd

from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


def _rating_a_clasificacion(rating) -> str | None:
    if pd.isna(rating):
        return None
    if rating >= 4:
        return "Positiva"
    if rating == 3:
        return "Neutra"
    if rating <= 2:
        return "Negativa"
    return None


def derivar_clasificacion_reviews(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"Derivando Clasificación desde Rating | filas={len(df)}")

    df = df.copy()
    df['Clasificación'] = df['Rating'].apply(_rating_a_clasificacion)

    sin_clasificar = df['Clasificación'].isna().sum()
    if sin_clasificar > 0:
        logger.warning(f"{sin_clasificar} filas sin Clasificación derivada (Rating nulo o fuera de 1-5)")

    distribucion = df['Clasificación'].value_counts(dropna=False).to_dict()
    logger.info(f"Distribución de Clasificación derivada: {distribucion}")

    return df
