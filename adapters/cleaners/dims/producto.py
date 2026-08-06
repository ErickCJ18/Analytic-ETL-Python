import pandas as pd

from adapters.cleaners.base_cleaner import (
    CleaningResult,
    limpiar_texto,
    convertir_entero,
    marcar_rechazadas,
    quitar_duplicados_en_archivo,
)
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


def limpiar_products(df_crudo: pd.DataFrame) -> CleaningResult:
    procesadas = len(df_crudo)

    df = df_crudo.copy()
    df["IdProducto"] = convertir_entero(df["IdProducto"])
    df["Nombre"] = limpiar_texto(df["Nombre"])
    df["Categoria"] = limpiar_texto(df["Categoría"])

    condiciones = {
        "IdProducto vacío o inválido": df["IdProducto"].isna(),
        "Nombre obligatorio": df["Nombre"].isna(),
        "Categoria obligatoria": df["Categoria"].isna(),
    }
    df_validas, df_rechazadas = marcar_rechazadas(df, condiciones)

    df_validas, dup_pk = quitar_duplicados_en_archivo(df_validas, "IdProducto")
    df_rechazadas = pd.concat([df_rechazadas, dup_pk], ignore_index=True)

    if not df_validas.empty:
        df_validas["IdProducto"] = df_validas["IdProducto"].astype(int)
        df_validas = df_validas[["IdProducto", "Nombre", "Categoria"]]

    resultado = CleaningResult("products", df_validas, df_rechazadas, procesadas)
    logger.info(resultado.resumen())
    return resultado
