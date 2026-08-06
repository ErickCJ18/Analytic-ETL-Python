import pandas as pd

from adapters.cleaners.base_cleaner import (
    CleaningResult,
    limpiar_texto,
    extraer_id_numerico,
    convertir_entero,
    convertir_fecha,
    marcar_rechazadas,
    quitar_duplicados_en_archivo,
)
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


def formatear_opiniones(df_base: pd.DataFrame) -> CleaningResult:
    logger.info(f"Iniciando limpieza de FactOpiniones | filas recibidas={len(df_base)}")

    df = df_base.copy()
    procesadas = len(df)

    df['IdCliente'] = extraer_id_numerico(df['IdCliente'])
    df['IdProducto'] = extraer_id_numerico(df['IdProducto'])
    df['Fecha'] = convertir_fecha(df['Fecha'])
    df['Comentario'] = limpiar_texto(df['Comentario'])
    df['Clasificación'] = limpiar_texto(df['Clasificación'])
    df['PuntajeSatisfacción'] = convertir_entero(df['PuntajeSatisfacción'])
    df['Fuente'] = limpiar_texto(df['Fuente'])

    logger.debug(f"Campos normalizados | columnas={list(df.columns)}")

    fuera_de_rango = df['PuntajeSatisfacción'].notna() & ~df['PuntajeSatisfacción'].between(1, 5)
    if fuera_de_rango.any():
        n = fuera_de_rango.sum()
        logger.warning(f"{n} valores de PuntajeSatisfacción fuera de rango (1-5); se ajustan al límite más cercano")
        df.loc[df['PuntajeSatisfacción'] > 5, 'PuntajeSatisfacción'] = 5
        df.loc[df['PuntajeSatisfacción'] < 1, 'PuntajeSatisfacción'] = 1

    condiciones = {
        "IdCliente nulo/invalido": df['IdCliente'].isna(),
        "IdProducto nulo/invalido": df['IdProducto'].isna(),
        "Fecha nula/invalida": df['Fecha'].isna(),
        "Clasificación nula": df['Clasificación'].isna(),
        "Fuente nula": df['Fuente'].isna(),
    }
    df_validas, df_rechazadas = marcar_rechazadas(df, condiciones)

    df_validas, df_dup = quitar_duplicados_en_archivo(df_validas, 'IdOpinion')
    if len(df_dup) > 0:
        logger.warning(f"{len(df_dup)} filas duplicadas por IdOpinion descartadas")
        df_rechazadas = pd.concat([df_rechazadas, df_dup], ignore_index=True)

    resultado = CleaningResult("FactOpiniones", df_validas, df_rechazadas, procesadas)
    logger.info(resultado.resumen())

    if resultado.rechazadas > 0:
        logger.warning(f"FactOpiniones tuvo {resultado.rechazadas} filas rechazadas")

    return resultado
