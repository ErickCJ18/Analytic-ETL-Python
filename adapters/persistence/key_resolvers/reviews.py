import pandas as pd
from sqlalchemy.engine import Engine

from adapters.persistence.dim_verification import verificar_dims_cargadas
from application.ports import SurrogateKeyResolver
from domain.entities import CleaningResult
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)

DIMS_REQUERIDAS_REVIEWS = [
    "DimCliente",
    "DimProducto",
    "DimOrigen",
    "DimFecha",
    "DimClasificacion",
]


def _leer_dim(engine: Engine, tabla: str, columnas: list[str]) -> pd.DataFrame:
    cols_sql = ", ".join(columnas)
    query = f"SELECT {cols_sql} FROM {tabla}"
    logger.debug(f"Leyendo dimensión {tabla} | columnas={columnas}")
    df = pd.read_sql(query, engine)
    logger.debug(f"{tabla} leída | filas={len(df)}")
    return df


def resolver_keys_reviews(df_clasificado: pd.DataFrame, engine: Engine) -> CleaningResult:
    verificar_dims_cargadas(engine, DIMS_REQUERIDAS_REVIEWS)

    logger.info(f"Iniciando resolución de surrogate keys para FactReviews | filas={len(df_clasificado)}")

    df = df_clasificado.copy()
    procesadas = len(df)

    df["NombreFuente"] = "SitioWebReviews"

    dim_cliente       = _leer_dim(engine, "DimCliente",       ["ClienteKey", "IdCliente"])
    dim_producto      = _leer_dim(engine, "DimProducto",      ["ProductoKey", "IdProducto"])
    dim_origen        = _leer_dim(engine, "DimOrigen",        ["OrigenKey", "NombreFuente"])
    dim_fecha         = _leer_dim(engine, "DimFecha",         ["FechaKey", "FullDate"])
    dim_clasificacion = _leer_dim(engine, "DimClasificacion", ["ClasificacionKey", "Clasificacion"])

    df = df.merge(dim_cliente, on="IdCliente", how="left")
    df = df.merge(dim_producto, on="IdProducto", how="left")
    df = df.merge(dim_origen, on="NombreFuente", how="left")
    df = df.merge(dim_fecha, left_on="Fecha", right_on="FullDate", how="left")
    df = df.merge(dim_clasificacion, left_on="Clasificación", right_on="Clasificacion", how="left")

    fk_cols = ["ClienteKey", "ProductoKey", "OrigenKey", "FechaKey", "ClasificacionKey"]
    condiciones_sin_match = df[fk_cols].isna().any(axis=1)

    df_rechazadas = df[condiciones_sin_match].copy()
    if len(df_rechazadas) > 0:
        motivos = df_rechazadas[fk_cols].isna().apply(
            lambda row: ", ".join([col for col in fk_cols if row[col]]), axis=1
        )
        df_rechazadas["MotivoRechazo"] = "Sin match en: " + motivos
        logger.warning(f"{len(df_rechazadas)} filas de FactReviews sin match en alguna dimensión")

    df_validas = df[~condiciones_sin_match].copy()

    df_validas = df_validas[[
        "ClienteKey", "ProductoKey", "OrigenKey", "FechaKey", "ClasificacionKey",
        "Comentario", "Rating"
    ]].copy()

    resultado = CleaningResult("FactReviews_Keys", df_validas, df_rechazadas, procesadas)
    logger.info(resultado.resumen())

    return resultado


class FactReviewsKeyResolver(SurrogateKeyResolver):
    def __init__(self, engine: Engine):
        self.engine = engine

    def resolve(self, df: pd.DataFrame) -> CleaningResult:
        return resolver_keys_reviews(df, self.engine)
