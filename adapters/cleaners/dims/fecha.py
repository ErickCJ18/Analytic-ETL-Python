import pandas as pd

from adapters.cleaners.base_cleaner import CleaningResult, marcar_rechazadas
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


def formatear_fecha(df_base: pd.DataFrame) -> CleaningResult:
    logger.info(f"Iniciando limpieza de DimFecha | filas recibidas={len(df_base)}")

    df = df_base.copy()
    procesadas = len(df)

    df['anio'] = df['FullDate'].dt.year
    df['trimestre'] = df['FullDate'].dt.quarter
    df['mes'] = df['FullDate'].dt.month
    df['semana'] = df['FullDate'].dt.isocalendar().week
    df['diaSemana'] = df['FullDate'].dt.dayofweek + 1
    df['esFinDeSemana'] = df['FullDate'].dt.dayofweek.isin([5, 6]).astype(int)

    condiciones = {
        "FullDate nula": df['FullDate'].isna(),
    }
    df_validas, df_rechazadas = marcar_rechazadas(df, condiciones)

    if df_validas['FullDate'].duplicated().any():
        n_dups = df_validas['FullDate'].duplicated().sum()
        logger.warning(f"Se encontraron {n_dups} fechas duplicadas en DimFecha; se descartan")
        dup_mask = df_validas['FullDate'].duplicated(keep='first')
        df_dup = df_validas[dup_mask].copy()
        df_dup['MotivoRechazo'] = 'Fecha duplicada'
        df_rechazadas = pd.concat([df_rechazadas, df_dup], ignore_index=True)
        df_validas = df_validas[~dup_mask].copy()

    df_validas['FullDate'] = df_validas['FullDate'].dt.date

    resultado = CleaningResult("DimFecha", df_validas, df_rechazadas, procesadas)
    logger.info(resultado.resumen())

    if resultado.rechazadas > 0:
        logger.warning(f"DimFecha tuvo {resultado.rechazadas} filas rechazadas")

    return resultado
