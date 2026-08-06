class CsvStructureError(Exception):
    """Se lanza cuando un CSV no tiene las columnas esperadas."""


class DimensionesNoCargadasError(Exception):
    """Se lanza cuando una o más dimensiones requeridas están vacías o no existen en la BD."""
