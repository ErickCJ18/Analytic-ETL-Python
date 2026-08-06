import pandas as pd


def contar_duplicados_archivo(df_rechazadas: pd.DataFrame) -> int:
    if df_rechazadas.empty or "MotivoRechazo" not in df_rechazadas.columns:
        return 0
    return int(df_rechazadas["MotivoRechazo"].str.startswith("Duplicado").sum())
