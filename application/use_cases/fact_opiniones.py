from collections.abc import Callable

import pandas as pd

from application.ports import CleanRepository, SurrogateKeyResolver
from application.use_cases.common import contar_duplicados_archivo
from domain.entities import CleaningResult, ResumenEntidad


def procesar_fact_opiniones(repo: CleanRepository,
                            source: Callable[[], pd.DataFrame],
                            cleaner: Callable[[pd.DataFrame], CleaningResult],
                            key_resolver: SurrogateKeyResolver) -> ResumenEntidad:
    r = cleaner(source())

    duplicados_archivo = contar_duplicados_archivo(r.df_rechazadas)
    rechazados = r.rechazadas - duplicados_archivo

    r_keys = key_resolver.resolve(r.df_validas)
    rechazados += r_keys.rechazadas

    df_nuevas, df_dup_bd = repo.dedup(r_keys.df_validas, "FactOpiniones",
                                      ["ClienteKey", "ProductoKey", "FechaKey"])
    insertados = repo.insert(df_nuevas, "FactOpiniones")

    return ResumenEntidad("FactOpiniones", r.procesadas, insertados,
                           duplicados_archivo + len(df_dup_bd), rechazados)
