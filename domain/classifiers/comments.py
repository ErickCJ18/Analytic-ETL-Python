import pandas as pd

from infrastructure.logging_setup import get_logger

logger = get_logger(__name__)

MAPA_CLASIFICACION_CONOCIDA = {
    "información suficiente, sin mayor novedad": "Neutra",
    "muy mala calidad, se rompió rápido": "Negativa",
    "gran relación calidad-precio": "Positiva",
    "pésima atención al cliente": "Negativa",
    "no cumple con lo anunciado, insatisfecho": "Negativa",
    "no funciona como esperaba, decepcionado": "Negativa",
    "me encanta este producto, excelente calidad": "Positiva",
    "muy satisfecho con la compra, lo recomiendo": "Positiva",
    "satisface lo básico": "Neutra",
    "entrega correcta, sin comentarios adicionales": "Neutra",
    "producto llegó rápido y funciona perfecto": "Positiva",
    "envío tardío y producto dañado": "Negativa",
    "calidad superior, muy contento": "Positiva",
    "es lo que esperaba, nada excepcional": "Neutra",
    "producto recibido, cumple su función": "Neutra",
}

PALABRAS_POSITIVAS = ['excelente', 'genial', 'recomendable', 'recomiendo', 'perfecto',
                       'encanta', 'increíble', 'contento', 'superior']
PALABRAS_NEGATIVAS = ['pésimo', 'pésima', 'terrible', 'rompió', 'decepcionado',
                       'dañado', 'no funciona', 'no cumple', 'tardío']


def _clasificar_fallback(texto: str) -> str:
    sp = sum(1 for p in PALABRAS_POSITIVAS if p in texto)
    sn = sum(1 for p in PALABRAS_NEGATIVAS if p in texto)
    if sp > sn:
        return "Positiva"
    if sn > sp:
        return "Negativa"
    return "Neutra"


def _clasificar_texto(comentario: str) -> str:
    if not comentario or pd.isna(comentario):
        return "Neutra"

    texto = comentario.strip().lower()

    if texto in MAPA_CLASIFICACION_CONOCIDA:
        return MAPA_CLASIFICACION_CONOCIDA[texto]

    logger.warning(f"Comentario no está en el mapa conocido, usando fallback: '{comentario[:60]}...'")
    return _clasificar_fallback(texto)


def derivar_clasificacion_comments(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"Derivando Clasificación desde Comentario | filas={len(df)}")

    df = df.copy()
    df['Clasificación'] = df['Comentario'].apply(_clasificar_texto)

    distribucion = df['Clasificación'].value_counts(dropna=False).to_dict()
    logger.info(f"Distribución de Clasificación derivada: {distribucion}")

    return df
