import pandas as pd

from domain.classifiers.comments import (
    _clasificar_fallback,
    _clasificar_texto,
    derivar_clasificacion_comments,
)
from domain.classifiers.reviews import _rating_a_clasificacion, derivar_clasificacion_reviews


def test_rating_a_clasificacion():
    assert _rating_a_clasificacion(5) == "Positiva"
    assert _rating_a_clasificacion(4) == "Positiva"
    assert _rating_a_clasificacion(3) == "Neutra"
    assert _rating_a_clasificacion(2) == "Negativa"
    assert _rating_a_clasificacion(1) == "Negativa"
    assert _rating_a_clasificacion(pd.NA) is None


def test_derivar_clasificacion_reviews():
    df = pd.DataFrame({"Rating": [5, 3, 1]})
    r = derivar_clasificacion_reviews(df)
    assert r["Clasificación"].tolist() == ["Positiva", "Neutra", "Negativa"]


def test_clasificar_texto_mapa_conocido():
    assert _clasificar_texto("ME ENCANTA este producto, excelente calidad") == "Positiva"
    assert _clasificar_texto("pésima atención al cliente") == "Negativa"
    assert _clasificar_texto("satisface lo básico") == "Neutra"


def test_clasificar_texto_fallback():
    assert _clasificar_fallback("excelente producto") == "Positiva"
    assert _clasificar_fallback("producto dañado") == "Negativa"


def test_derivar_clasificacion_comments():
    df = pd.DataFrame({"Comentario": ["gran relación calidad-precio", "envío tardío y producto dañado"]})
    r = derivar_clasificacion_comments(df)
    assert r["Clasificación"].tolist() == ["Positiva", "Negativa"]
