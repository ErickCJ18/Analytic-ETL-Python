from config.settings import DATA_DIR

from adapters.sources.base_reader import leer_csv

COLUMNAS_ESPERADAS = ["IdCliente", "Nombre", "Email"]

NOMBRE_ARCHIVO = "clients.csv"


def clientes_data_load_csv():
    ruta = DATA_DIR / NOMBRE_ARCHIVO
    return leer_csv(ruta, COLUMNAS_ESPERADAS)
