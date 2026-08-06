import pandas as pd

from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)

CATALOGO_ORIGEN = [
    {'NombreFuente': 'EncuestaInterna', 'TipoCanal': 'Encuesta'},
    {'NombreFuente': 'Instagram',       'TipoCanal': 'RedSocial'},
    {'NombreFuente': 'Twitter',         'TipoCanal': 'RedSocial'},
    {'NombreFuente': 'Facebook',        'TipoCanal': 'RedSocial'},
    {'NombreFuente': 'SitioWebReviews', 'TipoCanal': 'Web'},
]


def origen_data_load():
    logger.info(f"Generando catálogo DimOrigen | total_valores={len(CATALOGO_ORIGEN)}")
    df_origen = pd.DataFrame(CATALOGO_ORIGEN)
    return df_origen
