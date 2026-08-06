import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from application.ports import CleanRepository
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


class SqlCleanRepository(CleanRepository):
    def __init__(self, engine: Engine):
        self.engine = engine

    def dedup(self, df: pd.DataFrame, table_name: str, pk_column) -> tuple[pd.DataFrame, pd.DataFrame]:
        if df.empty:
            return df, df

        columnas = pk_column if isinstance(pk_column, list) else [pk_column]
        cols_sql = ", ".join(columnas)

        query = text(f"SELECT {cols_sql} FROM {table_name}")
        with self.engine.connect() as conn:
            if len(columnas) == 1:
                existentes = set(row[0] for row in conn.execute(query))
            else:
                existentes = set(tuple(row) for row in conn.execute(query))

        if len(columnas) == 1:
            es_dup = df[columnas[0]].isin(existentes)
        else:
            es_dup = df[columnas].apply(tuple, axis=1).isin(existentes)

        return df[~es_dup].copy(), df[es_dup].copy()

    def insert(self, df: pd.DataFrame, table_name: str) -> int:
        if df.empty:
            return 0
        df.to_sql(
            table_name, con=self.engine, if_exists="append", index=False,
            chunksize=500,
        )
        logger.info(f"{table_name}: {len(df)} fila(s) insertada(s)")
        return len(df)
