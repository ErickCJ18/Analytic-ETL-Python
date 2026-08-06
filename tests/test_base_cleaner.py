import pandas as pd
import pytest

from adapters.cleaners.base_cleaner import (
    convertir_entero,
    convertir_fecha,
    extraer_id_numerico,
    limpiar_texto,
    marcar_rechazadas,
    quitar_duplicados_en_archivo,
)


def test_limpiar_texto_quita_espacios_y_vacios():
    s = pd.Series(["  Hola  ", "", "  ", "Texto", None])
    r = limpiar_texto(s)
    assert r.iloc[0] == "Hola"
    assert pd.isna(r.iloc[1])
    assert pd.isna(r.iloc[2])
    assert r.iloc[3] == "Texto"
    assert pd.isna(r.iloc[4])


def test_convertir_entero():
    s = pd.Series(["42", "  7 ", "abc", None, "12.5"])
    r = convertir_entero(s)
    assert r.iloc[0] == 42
    assert r.iloc[1] == 7
    assert pd.isna(r.iloc[2])
    assert pd.isna(r.iloc[3])
    assert pd.isna(r.iloc[4])


def test_extraer_id_numerico():
    s = pd.Series(["A123", "B456", "sin-numero", None, "789"])
    r = extraer_id_numerico(s)
    assert r.iloc[0] == 123
    assert r.iloc[1] == 456
    assert pd.isna(r.iloc[2])
    assert pd.isna(r.iloc[3])
    assert r.iloc[4] == 789


def test_convertir_fecha():
    s = pd.Series(["2024-09-13", "no-valida", None])
    r = convertir_fecha(s)
    assert str(r.iloc[0]) == "2024-09-13"
    assert pd.isna(r.iloc[1])
    assert pd.isna(r.iloc[2])


def test_marcar_rechazadas():
    df = pd.DataFrame({
        "a": [1, 2, 3, 4],
        "b": ["x", "", "y", "z"],
    })
    condiciones = {"b vacía": df["b"] == ""}
    validas, rechazadas = marcar_rechazadas(df, condiciones)
    assert len(validas) == 3
    assert len(rechazadas) == 1
    assert rechazadas.iloc[0]["MotivoRechazo"] == "b vacía"


def test_quitar_duplicados_en_archivo():
    df = pd.DataFrame({"id": [1, 2, 2, 3]})
    validas, duplicados = quitar_duplicados_en_archivo(df, "id")
    assert len(validas) == 3
    assert len(duplicados) == 1
    assert duplicados.iloc[0]["MotivoRechazo"].startswith("Duplicado")


def test_quitar_duplicados_en_archivo_vacio():
    df = pd.DataFrame({"id": []})
    validas, duplicados = quitar_duplicados_en_archivo(df, "id")
    assert validas.empty
    assert duplicados.empty
