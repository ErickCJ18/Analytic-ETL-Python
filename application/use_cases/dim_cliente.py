from collections.abc import Callable

import pandas as pd

from application.ports import CleanRepository
from application.use_cases.common import contar_duplicados_archivo
from domain.entities import CleaningResult, ResumenEntidad


def procesar_dim_cliente(repo: CleanRepository,
                         source: Callable[[], pd.DataFrame],
                         cleaner: Callable[[pd.DataFrame], CleaningResult]) -> ResumenEntidad:
    r = cleaner(source())

    duplicados_archivo = contar_duplicados_archivo(r.df_rechazadas)
    rechazados = r.rechazadas - duplicados_archivo

    df_nuevas, df_dup_bd = repo.dedup(r.df_validas, "DimCliente", "IdCliente")
    insertados = repo.insert(df_nuevas, "DimCliente")

    return ResumenEntidad("DimCliente", r.procesadas, insertados,
                           duplicados_archivo + len(df_dup_bd), rechazados)
