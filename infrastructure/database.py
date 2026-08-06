from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from config.settings import (
    DB_DRIVER, DB_SERVER, DB_DATABASE, DB_TRUSTED_CONNECTION,
    DB_USER, DB_PASSWORD,
)
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)

_engine: Engine | None = None


def _build_conn_str() -> str:
    parts = [f"DRIVER={DB_DRIVER}", f"SERVER={DB_SERVER}", f"DATABASE={DB_DATABASE}"]

    if DB_TRUSTED_CONNECTION.lower() == "yes":
        parts.append("Trusted_Connection=yes")
    else:
        if not DB_USER or not DB_PASSWORD:
            raise RuntimeError(
                "DB_TRUSTED_CONNECTION=no requiere DB_USER y DB_PASSWORD en el .env"
            )
        parts.append(f"UID={DB_USER}")
        parts.append(f"PWD={DB_PASSWORD}")

    return ";".join(parts) + ";"


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        conn_str = _build_conn_str()
        odbc_connect = quote_plus(conn_str)
        url = f"mssql+pyodbc:///?odbc_connect={odbc_connect}"
        _engine = create_engine(url, pool_pre_ping=True, fast_executemany=True)
        logger.info("Engine de SQLAlchemy creado")
    return _engine
