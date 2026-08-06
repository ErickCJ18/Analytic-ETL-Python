from pathlib import Path
from typing import List

import pandas as pd

from domain.exceptions import CsvStructureError
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


def leer_csv(ruta: Path, columnas_esperadas: List[str]) -> pd.DataFrame:
    if not ruta.exists():
        logger.error(f"Archivo no encontrado: {ruta}")
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    logger.info(f"Leyendo archivo: {ruta.name}")

    try:
        df = pd.read_csv(ruta, dtype=str, encoding="utf-8")
    except Exception as ex:
        logger.error(f"No se pudo leer '{ruta.name}': {ex}")
        raise

    faltantes = [c for c in columnas_esperadas if c not in df.columns]
    if faltantes:
        logger.error(f"{ruta.name}: columnas faltantes {faltantes}")
        raise CsvStructureError(
            f"El archivo '{ruta.name}' no tiene las columnas esperadas. "
            f"Faltan: {faltantes}. Columnas encontradas: {list(df.columns)}"
        )

    logger.info(f"{ruta.name}: {len(df)} fila(s) leída(s), estructura válida")
    return df
