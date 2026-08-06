import pandas as pd

from adapters.cleaners.base_cleaner import CleaningResult, limpiar_texto
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


def formatear_clasificacion(df_base: pd.DataFrame) -> CleaningResult:
    logger.info(f"Iniciando limpieza de DimClasificacion | filas recibidas={len(df_base)}")

    df = df_base.copy()
    procesadas = len(df)

    df['Clasificacion'] = limpiar_texto(df['Clasificacion'])

    df_rechazadas = df[df['Clasificacion'].isna()].copy()
    df_rechazadas['MotivoRechazo'] = 'Clasificacion nula o vacía'

    df_validas = df[df['Clasificacion'].notna()].drop_duplicates(subset=['Clasificacion']).copy()

    if len(df_validas) < len(df) - len(df_rechazadas):
        logger.warning("Se encontraron valores duplicados en DimClasificacion; se descartaron")

    resultado = CleaningResult("DimClasificacion", df_validas, df_rechazadas, procesadas)
    logger.info(resultado.resumen())

    return resultado
