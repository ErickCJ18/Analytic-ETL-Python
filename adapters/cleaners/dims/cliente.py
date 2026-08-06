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

REGEX_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


def limpiar_clientes(df_crudo: pd.DataFrame) -> CleaningResult:
    procesadas = len(df_crudo)

    df = df_crudo.copy()
    df["IdCliente"] = convertir_entero(df["IdCliente"])
    df["Nombre"] = limpiar_texto(df["Nombre"])
    df["Email"] = limpiar_texto(df["Email"])

    condiciones = {
        "IdCliente vacío o inválido": df["IdCliente"].isna(),
        "Nombre obligatorio": df["Nombre"].isna(),
        "Email obligatorio": df["Email"].isna(),
        "Email con formato inválido": df["Email"].notna() & ~df["Email"].str.match(REGEX_EMAIL, na=False),
    }
    df_validas, df_rechazadas = marcar_rechazadas(df, condiciones)

    df_validas, dup_pk = quitar_duplicados_en_archivo(df_validas, "IdCliente")

    es_dup_email = df_validas.duplicated(subset=["Email"], keep="first")
    dup_email = df_validas[es_dup_email].copy()
    dup_email["MotivoRechazo"] = "Email duplicado dentro del archivo"
    df_validas = df_validas[~es_dup_email]

    df_rechazadas = pd.concat([df_rechazadas, dup_pk, dup_email], ignore_index=True)

    if not df_validas.empty:
        df_validas["IdCliente"] = df_validas["IdCliente"].astype(int)
        df_validas = df_validas[["IdCliente", "Nombre", "Email"]]

    resultado = CleaningResult("DimCliente", df_validas, df_rechazadas, procesadas)
    logger.info(resultado.resumen())
    return resultado
