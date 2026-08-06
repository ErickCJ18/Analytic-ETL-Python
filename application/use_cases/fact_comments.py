from collections.abc import Callable

import pandas as pd

from application.ports import CleanRepository, SurrogateKeyResolver
from application.use_cases.common import contar_duplicados_archivo
from domain.entities import CleaningResult, ResumenEntidad


def procesar_fact_comments(repo: CleanRepository,
                           source: Callable[[], pd.DataFrame],
                           cleaner: Callable[[pd.DataFrame], CleaningResult],
                           classifier: Callable[[pd.DataFrame], pd.DataFrame],
                           key_resolver: SurrogateKeyResolver) -> ResumenEntidad:
    r = cleaner(source())

    duplicados_archivo = contar_duplicados_archivo(r.df_rechazadas)
    rechazados = r.rechazadas - duplicados_archivo

    df_clasificado = classifier(r.df_validas)
    r_keys = key_resolver.resolve(df_clasificado)
    rechazados += r_keys.rechazadas

    df_nuevas, df_dup_bd = repo.dedup(r_keys.df_validas, "FactComments",
                                      ["ClienteKey", "ProductoKey", "FechaKey"])
    insertados = repo.insert(df_nuevas, "FactComments")

    return ResumenEntidad("FactComments", r.procesadas, insertados,
                           duplicados_archivo + len(df_dup_bd), rechazados)
