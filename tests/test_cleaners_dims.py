import pandas as pd

from adapters.cleaners.dims.cliente import limpiar_clientes
from adapters.cleaners.dims.producto import limpiar_products


def test_limpiar_clientes_validos_y_rechazos():
    df = pd.DataFrame({
        "IdCliente": [1, 2, 3, 4, 5, 6],
        "Nombre": ["Ana", "Luis", "  ", "Carlos", "Maria", "Juan"],
        "Email": ["ana@mail.com", "luis@mail.com", "car@mail.com", "sin-formato", "dup@mail.com", "dup@mail.com"],
    })
    r = limpiar_clientes(df)
    assert r.procesadas == 6
    assert r.validas == 3
    assert r.rechazadas == 3
    motivos = r.df_rechazadas["MotivoRechazo"].tolist()
    assert any("Nombre obligatorio" in m for m in motivos)
    assert any("formato" in m for m in motivos)
    assert any("Email duplicado" in m for m in motivos)


def test_limpiar_clientes_duplicado_pk():
    df = pd.DataFrame({
        "IdCliente": [1, 1],
        "Nombre": ["Ana", "Ana"],
        "Email": ["a@m.com", "b@m.com"],
    })
    r = limpiar_clientes(df)
    assert r.validas == 1
    assert r.rechazadas == 1
    assert "Duplicado" in r.df_rechazadas.iloc[0]["MotivoRechazo"]


def test_limpiar_products_valido_y_rechazo():
    df = pd.DataFrame({
        "IdProducto": [1, 2, 3],
        "Nombre": ["Laptop", "Mouse", "Teclado"],
        "Categoría": ["Computo", "  ", "Accesorios"],
    })
    r = limpiar_products(df)
    assert r.procesadas == 3
    assert r.validas == 2
    assert r.rechazadas == 1
    assert list(r.df_validas.columns) == ["IdProducto", "Nombre", "Categoria"]
