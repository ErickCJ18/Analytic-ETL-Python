import pandas as pd

from adapters.cleaners.base_cleaner import CleaningResult, limpiar_texto
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


def formatear_origen(df_base: pd.DataFrame) -> CleaningResult:
    logger.info(f"Iniciando limpieza de DimOrigen | filas recibidas={len(df_base)}")

    df = df_base.copy()
    procesadas = len(df)

    df['NombreFuente'] = limpiar_texto(df['NombreFuente'])
    df['TipoCanal'] = limpiar_texto(df['TipoCanal'])

    df_rechazadas = df[df['NombreFuente'].isna()].copy()
    df_rechazadas['MotivoRechazo'] = 'NombreFuente nula o vacía'

    df_validas = df[df['NombreFuente'].notna()].drop_duplicates(subset=['NombreFuente']).copy()

    resultado = CleaningResult("DimOrigen", df_validas, df_rechazadas, procesadas)
    logger.info(resultado.resumen())

    return resultado
