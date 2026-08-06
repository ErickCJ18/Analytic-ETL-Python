import asyncio
from functools import partial

from application.ports import CleanRepository, SurrogateKeyResolver
from application.use_cases.dim_cliente import procesar_dim_cliente
from application.use_cases.dim_clasificacion import procesar_dim_clasificacion
from application.use_cases.dim_fecha import procesar_dim_fecha
from application.use_cases.dim_origen import procesar_dim_origen
from application.use_cases.dim_producto import procesar_dim_producto
from application.use_cases.fact_comments import procesar_fact_comments
from application.use_cases.fact_opiniones import procesar_fact_opiniones
from application.use_cases.fact_reviews import procesar_fact_reviews
from config.settings import MAX_WORKERS
from adapters.cleaners.dims.cliente import limpiar_clientes
from adapters.cleaners.dims.clasificacion import formatear_clasificacion
from adapters.cleaners.dims.fecha import formatear_fecha
from adapters.cleaners.dims.origen import formatear_origen
from adapters.cleaners.dims.producto import limpiar_products
from adapters.cleaners.facts.comments import formatear_comments
from adapters.cleaners.facts.opiniones import formatear_opiniones
from adapters.cleaners.facts.reviews import formatear_reviews
from adapters.persistence.key_resolvers.comments import FactCommentsKeyResolver
from adapters.persistence.key_resolvers.opiniones import FactOpinionesKeyResolver
from adapters.persistence.key_resolvers.reviews import FactReviewsKeyResolver
from adapters.persistence.sql_repository import SqlCleanRepository
from adapters.sources.dims.cliente import clientes_data_load_csv
from adapters.sources.dims.clasificacion import generar_dim_clasificacion
from adapters.sources.dims.fecha import fecha_data_load
from adapters.sources.dims.origen import origen_data_load
from adapters.sources.dims.producto import cargar_products_csv
from adapters.sources.facts.comments import comments_data_load
from adapters.sources.facts.opiniones import opiniones_data_load
from adapters.sources.facts.reviews import reviews_data_load
from domain.entities import ResumenEntidad
from domain.classifiers.comments import derivar_clasificacion_comments
from domain.classifiers.reviews import derivar_clasificacion_reviews
from infrastructure.database import get_engine
from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)


def _procesos_dims(repo: CleanRepository) -> list:
    return [
        partial(procesar_dim_fecha, repo, fecha_data_load, formatear_fecha),
        partial(procesar_dim_clasificacion, repo, generar_dim_clasificacion, formatear_clasificacion),
        partial(procesar_dim_origen, repo, origen_data_load, formatear_origen),
        partial(procesar_dim_cliente, repo, clientes_data_load_csv, limpiar_clientes),
        partial(procesar_dim_producto, repo, cargar_products_csv, limpiar_products),
    ]


def _procesos_facts(repo: CleanRepository) -> list:
    return [
        partial(
            procesar_fact_opiniones, repo, opiniones_data_load, formatear_opiniones,
            FactOpinionesKeyResolver(repo.engine),
        ),
        partial(
            procesar_fact_reviews, repo, reviews_data_load, formatear_reviews,
            derivar_clasificacion_reviews, FactReviewsKeyResolver(repo.engine),
        ),
        partial(
            procesar_fact_comments, repo, comments_data_load, formatear_comments,
            derivar_clasificacion_comments, FactCommentsKeyResolver(repo.engine),
        ),
    ]


def imprimir_resumen_final(resumenes: list[ResumenEntidad]) -> None:
    print("\n" + "=" * 80)
    print("RESUMEN FINAL DEL PROCESO ETL OLAP")
    print("=" * 80)
    print(f"{'Entidad':20s} | {'Procesados':>10s} | {'Insertados':>10s} | {'Duplicados':>10s} | {'Rechazados':>10s}")
    print("-" * 80)

    totales = {"procesados": 0, "insertados": 0, "duplicados": 0, "rechazados": 0}
    for r in resumenes:
        print(f"{r.entidad:20s} | {r.procesados:10d} | {r.insertados:10d} | {r.duplicados:10d} | {r.rechazados:10d}")
        totales["procesados"] += r.procesados
        totales["insertados"] += r.insertados
        totales["duplicados"] += r.duplicados
        totales["rechazados"] += r.rechazados

    print("-" * 80)
    print(f"{'TOTAL':20s} | {totales['procesados']:10d} | {totales['insertados']:10d} | "
          f"{totales['duplicados']:10d} | {totales['rechazados']:10d}")


async def _ejecutar_proceso(procesar) -> ResumenEntidad | None:
    logger.info(f"=== Iniciando: {procesar.func.__name__} ===")
    try:
        resumen = await asyncio.to_thread(procesar)
        logger.info(resumen.resumen())
        return resumen
    except Exception as ex:
        logger.exception(f"Fallo crítico en {procesar.func.__name__}: {ex}")
        return None


async def _ejecutar_concurrente(procesos: list, max_workers: int | None) -> list[ResumenEntidad]:
    semaforo = asyncio.Semaphore(max_workers) if max_workers else None

    async def _tarea(procesar) -> ResumenEntidad | None:
        if semaforo is None:
            return await _ejecutar_proceso(procesar)
        async with semaforo:
            return await _ejecutar_proceso(procesar)

    resumenes = await asyncio.gather(*(_tarea(p) for p in procesos))
    return [r for r in resumenes if r is not None]


async def main() -> None:
    engine = get_engine()
    repo = SqlCleanRepository(engine)

    logger.info("=== FASE 1: dimensiones (en paralelo) ===")
    resumenes_dims = await _ejecutar_concurrente(_procesos_dims(repo), MAX_WORKERS)

    logger.info("=== FASE 2: hechos (en paralelo, requieren dimensiones cargadas) ===")
    resumenes_facts = await _ejecutar_concurrente(_procesos_facts(repo), MAX_WORKERS)

    imprimir_resumen_final(resumenes_dims + resumenes_facts)


if __name__ == "__main__":
    asyncio.run(main())
