from config.settings import DATA_DIR

from adapters.sources.base_reader import leer_csv

COLUMNAS_ESPERADAS = ["IdProducto", "Nombre", "Categoría"]

NOMBRE_ARCHIVO = "products.csv"


def cargar_products_csv():
    ruta = DATA_DIR / NOMBRE_ARCHIVO
    return leer_csv(ruta, COLUMNAS_ESPERADAS)
