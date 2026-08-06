import pandas as pd

from adapters.cleaners.dims.cliente import limpiar_clientes
from adapters.cleaners.facts.opiniones import formatear_opiniones
from adapters.cleaners.facts.reviews import formatear_reviews
from application.use_cases.dim_cliente import procesar_dim_cliente
from application.use_cases.fact_opiniones import procesar_fact_opiniones
from application.use_cases.fact_reviews import procesar_fact_reviews
from domain.classifiers.reviews import derivar_clasificacion_reviews
from domain.entities import CleaningResult


class FakeRepo:
    def __init__(self, existentes: set | None = None):
        self.existentes = existentes or set()
        self.insert_calls = []

    def dedup(self, df, table_name, pk_column):
        if df.empty:
            return df, df
        columnas = pk_column if isinstance(pk_column, list) else [pk_column]
        if len(columnas) == 1:
            es_dup = df[columnas[0]].isin(self.existentes)
        else:
            es_dup = df[columnas].apply(tuple, axis=1).isin(self.existentes)
        return df[~es_dup].copy(), df[es_dup].copy()

    def insert(self, df, table_name):
        self.insert_calls.append((table_name, len(df)))
        return len(df)


class FakeKeyResolver:
    def resolve(self, df: pd.DataFrame) -> CleaningResult:
        out = df.copy()
        out["ClienteKey"] = out["IdCliente"]
        out["ProductoKey"] = out["IdProducto"]
        out["FechaKey"] = range(1, len(out) + 1)
        return CleaningResult("keys", out, out.iloc[0:0].copy(), len(out))


def fuente_clientes():
    return pd.DataFrame({
        "IdCliente": [1, 2],
        "Nombre": ["Ana", "Luis"],
        "Email": ["ana@mail.com", "luis@mail.com"],
    })


def test_procesar_dim_cliente_inserta_y_cuenta():
    repo = FakeRepo(existentes={1})
    r = procesar_dim_cliente(repo, fuente_clientes, limpiar_clientes)
    assert r.procesados == 2
    assert r.insertados == 1
    assert r.duplicados == 1
    assert r.rechazados == 0
    assert repo.insert_calls == [("DimCliente", 1)]


def fuente_opiniones():
    return pd.DataFrame({
        "IdOpinion": [1, 2],
        "IdCliente": ["C1", "C2"],
        "IdProducto": ["P1", "P2"],
        "Fecha": ["2024-09-13", "2024-09-14"],
        "Comentario": ["bien", "mal"],
        "Clasificación": ["Positiva", "Negativa"],
        "PuntajeSatisfacción": [5, 2],
        "Fuente": ["EncuestaInterna", "EncuestaInterna"],
    })


def test_procesar_fact_opiniones_orquesta():
    repo = FakeRepo()
    r = procesar_fact_opiniones(repo, fuente_opiniones, formatear_opiniones, FakeKeyResolver())
    assert r.procesados == 2
    assert r.insertados == 2
    assert r.duplicados == 0
    assert r.rechazados == 0


def test_procesar_fact_reviews_orquesta_con_clasificador():
    repo = FakeRepo()

    def fuente_reviews():
        return pd.DataFrame({
            "IdReview": [1, 2],
            "IdCliente": ["C1", "C2"],
            "IdProducto": ["P1", "P2"],
            "Fecha": ["2024-09-13", "2024-09-14"],
            "Comentario": ["ok", "mal"],
            "Rating": [5, 1],
        })

    r = procesar_fact_reviews(repo, fuente_reviews, formatear_reviews, derivar_clasificacion_reviews, FakeKeyResolver())
    assert r.procesados == 2
    assert r.insertados == 2
