from sqlalchemy import text
from sqlalchemy.engine import Engine

from domain.exceptions import DimensionesNoCargadasError
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)

DIMS_REQUERIDAS_OPINIONES = [
    "DimCliente",
    "DimProducto",
    "DimOrigen",
    "DimFecha",
    "DimClasificacion",
]

DIMS_REQUERIDAS_REVIEWS = [
    "DimCliente",
    "DimProducto",
    "DimOrigen",
    "DimFecha",
    "DimClasificacion",
]

DIMS_REQUERIDAS_COMMENTS = [
    "DimCliente",
    "DimProducto",
    "DimOrigen",
    "DimFecha",
    "DimClasificacion",
]


def verificar_dims_cargadas(engine: Engine, dims: list[str]) -> dict[str, int]:
    logger.info(f"Verificando estado de dimensiones antes de resolver keys | dims={dims}")
    conteos = {}
    faltantes = []

    with engine.connect() as conn:
        for tabla in dims:
            try:
                resultado = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                count = resultado.scalar()
                conteos[tabla] = count
                if count == 0:
                    faltantes.append(tabla)
                    logger.warning(f"{tabla} existe pero está VACÍA (0 filas)")
                else:
                    logger.info(f"{tabla} verificada | filas={count}")
            except Exception as e:
                faltantes.append(tabla)
                logger.error(f"No se pudo verificar {tabla}: {e}")

    if faltantes:
        mensaje = f"Dimensiones no cargadas o vacías: {faltantes}"
        logger.error(mensaje)
        raise DimensionesNoCargadasError(mensaje)

    logger.info("Todas las dimensiones requeridas están cargadas correctamente")
    return conteos
