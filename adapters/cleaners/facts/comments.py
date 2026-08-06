import pandas as pd

from adapters.cleaners.base_cleaner import (
    CleaningResult,
    limpiar_texto,
    extraer_id_numerico,
    convertir_fecha,
    marcar_rechazadas,
    quitar_duplicados_en_archivo,
)
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


def formatear_comments(df_base: pd.DataFrame) -> CleaningResult:
    logger.info(f"Iniciando limpieza de FactComments | filas recibidas={len(df_base)}")

    df = df_base.copy()
    procesadas = len(df)

    df['IdCliente'] = extraer_id_numerico(df['IdCliente'])
    df['IdProducto'] = extraer_id_numerico(df['IdProducto'])
    df['Fecha'] = convertir_fecha(df['Fecha'])
    df['Comentario'] = limpiar_texto(df['Comentario'])
    df['Fuente'] = limpiar_texto(df['Fuente'])

    condiciones = {
        "IdCliente nulo/invalido": df['IdCliente'].isna(),
        "IdProducto nulo/invalido": df['IdProducto'].isna(),
        "Fecha nula/invalida": df['Fecha'].isna(),
        "Fuente nula": df['Fuente'].isna(),
    }
    df_validas, df_rechazadas = marcar_rechazadas(df, condiciones)

    df_validas, df_dup = quitar_duplicados_en_archivo(df_validas, 'IdComment')
    if len(df_dup) > 0:
        logger.warning(f"{len(df_dup)} filas duplicadas por IdComment descartadas")
        df_rechazadas = pd.concat([df_rechazadas, df_dup], ignore_index=True)

    resultado = CleaningResult("FactComments", df_validas, df_rechazadas, procesadas)
    logger.info(resultado.resumen())

    if resultado.rechazadas > 0:
        logger.warning(f"FactComments tuvo {resultado.rechazadas} filas rechazadas")

    return resultado
