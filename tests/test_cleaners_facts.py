import pandas as pd

from adapters.cleaners.facts.comments import formatear_comments
from adapters.cleaners.facts.opiniones import formatear_opiniones
from adapters.cleaners.facts.reviews import formatear_reviews


def test_formatear_opiniones_clamping_y_rechazos():
    df = pd.DataFrame({
        "IdOpinion": [1, 2, 3],
        "IdCliente": ["C1", "C2", "C3"],
        "IdProducto": ["P1", "P2", "P3"],
        "Fecha": ["2024-09-13", "2024-09-14", "mal"],
        "Comentario": ["bien", "mal", "regular"],
        "Clasificación": ["Positiva", "Negativa", "Neutra"],
        "PuntajeSatisfacción": [5, 0, 3],
        "Fuente": ["EncuestaInterna", "EncuestaInterna", "EncuestaInterna"],
    })
    r = formatear_opiniones(df)
    assert r.procesadas == 3
    assert r.rechazadas == 1
    # El 0 fuera de rango debe quedar clampeado a 1 y la fila válida
    puntaje = r.df_validas.set_index("IdOpinion").loc[2, "PuntajeSatisfacción"]
    assert puntaje == 1


def test_formatear_reviews_duplicados():
    df = pd.DataFrame({
        "IdReview": [1, 1],
        "IdCliente": ["C1", "C1"],
        "IdProducto": ["P1", "P1"],
        "Fecha": ["2024-09-13", "2024-09-13"],
        "Comentario": ["ok", "ok"],
        "Rating": [4, 4],
    })
    r = formatear_reviews(df)
    assert r.validas == 1
    assert r.rechazadas == 1
    assert "Duplicado" in r.df_rechazadas.iloc[0]["MotivoRechazo"]


def test_formatear_comments_rechazo_por_fuente():
    df = pd.DataFrame({
        "IdComment": [1],
        "IdCliente": ["C1"],
        "IdProducto": ["P1"],
        "Fecha": ["2024-09-13"],
        "Comentario": ["ok"],
        "Fuente": [None],
    })
    r = formatear_comments(df)
    assert r.validas == 0
    assert r.rechazadas == 1
    assert "Fuente nula" in r.df_rechazadas.iloc[0]["MotivoRechazo"]
