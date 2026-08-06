from abc import ABC, abstractmethod

import pandas as pd

from domain.entities import CleaningResult


class CleanRepository(ABC):
    """Puerto de persistencia: separa qué filas ya existen y sube las nuevas."""

    @abstractmethod
    def dedup(self, df: pd.DataFrame, table_name: str, pk_column) -> tuple[pd.DataFrame, pd.DataFrame]:
        ...

    @abstractmethod
    def insert(self, df: pd.DataFrame, table_name: str) -> int:
        ...


class SurrogateKeyResolver(ABC):
    """Puerto de resolución de surrogate keys contra las dimensiones cargadas."""

    @abstractmethod
    def resolve(self, df: pd.DataFrame) -> CleaningResult:
        ...
