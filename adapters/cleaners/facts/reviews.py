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


def formatear_reviews(df_base: pd.DataFrame) -> CleaningResult:
    logger.info(f"Iniciando limpieza de FactReviews | filas recibidas={len(df_base)}")

    df = df_base.copy()
    procesadas = len(df)

    df['IdCliente'] = extraer_id_numerico(df['IdCliente'])
    df['IdProducto'] = extraer_id_numerico(df['IdProducto'])
    df['Fecha'] = convertir_fecha(df['Fecha'])
    df['Comentario'] = limpiar_texto(df['Comentario'])
    df['Rating'] = convertir_entero(df['Rating'])

    fuera_de_rango = df['Rating'].notna() & ~df['Rating'].between(1, 5)
    if fuera_de_rango.any():
        n = fuera_de_rango.sum()
        logger.warning(f"{n} valores de Rating fuera de rango (1-5); se ajustan al límite más cercano")
        df.loc[df['Rating'] > 5, 'Rating'] = 5
        df.loc[df['Rating'] < 1, 'Rating'] = 1

    condiciones = {
        "IdCliente nulo/invalido": df['IdCliente'].isna(),
        "IdProducto nulo/invalido": df['IdProducto'].isna(),
        "Fecha nula/invalida": df['Fecha'].isna(),
    }
    df_validas, df_rechazadas = marcar_rechazadas(df, condiciones)

    df_validas, df_dup = quitar_duplicados_en_archivo(df_validas, 'IdReview')
    if len(df_dup) > 0:
        logger.warning(f"{len(df_dup)} filas duplicadas por IdReview descartadas")
        df_rechazadas = pd.concat([df_rechazadas, df_dup], ignore_index=True)

    resultado = CleaningResult("FactReviews", df_validas, df_rechazadas, procesadas)
    logger.info(resultado.resumen())

    return resultado
