import re

import pandas as pd

from domain.entities import CleaningResult


def limpiar_texto(series: pd.Series) -> pd.Series:
    limpio = series.astype("object").str.strip()
    return limpio.replace("", pd.NA)


def convertir_entero(series: pd.Series) -> pd.Series:
    def _parse(valor):
        if pd.isna(valor):
            return pd.NA
        try:
            return int(str(valor).strip())
        except ValueError:
            return pd.NA

    return series.map(_parse)


def extraer_id_numerico(series: pd.Series) -> pd.Series:
    def _parse(valor):
        if pd.isna(valor):
            return pd.NA
        coincidencia = re.search(r"\d+", str(valor))
        if coincidencia is None:
            return pd.NA
        return int(coincidencia.group())

    return series.map(_parse)


def convertir_fecha(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce").dt.date


def marcar_rechazadas(df: pd.DataFrame, condiciones: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    rechazada = pd.Series(False, index=df.index, dtype=bool)
    motivos = pd.Series([[] for _ in df.index], index=df.index, dtype=object)

    for motivo, condicion in condiciones.items():
        mask = pd.Series(condicion, index=df.index).fillna(False).astype(bool)
        rechazada = rechazada | mask
        for idx in df.index[mask.to_numpy()]:
            motivos.at[idx].append(motivo)

    df_rechazadas = df[rechazada].copy()
    df_rechazadas["MotivoRechazo"] = [", ".join(m) for m in motivos[rechazada].tolist()]
    df_validas = df[~rechazada].copy()
    return df_validas, df_rechazadas


def quitar_duplicados_en_archivo(df: pd.DataFrame, columna: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty:
        return df.copy(), df.copy()

    es_duplicado = df[columna].duplicated(keep="first")
    df_validas = df[~es_duplicado].copy()
    df_duplicados = df[es_duplicado].copy()
    df_duplicados["MotivoRechazo"] = f"Duplicado por {columna} dentro del archivo"
    return df_validas, df_duplicados
