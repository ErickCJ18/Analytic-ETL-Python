from dataclasses import dataclass

import pandas as pd


@dataclass
class CleaningResult:
    entidad: str
    df_validas: pd.DataFrame
    df_rechazadas: pd.DataFrame
    procesadas: int

    @property
    def validas(self) -> int:
        return len(self.df_validas)

    @property
    def rechazadas(self) -> int:
        return len(self.df_rechazadas)

    def resumen(self) -> str:
        return (
            f"{self.entidad}: procesadas={self.procesadas}, "
            f"validas={self.validas}, rechazadas={self.rechazadas}"
        )


@dataclass
class ResumenEntidad:
    entidad: str
    procesados: int
    insertados: int
    duplicados: int
    rechazados: int

    def resumen(self) -> str:
        return (
            f"{self.entidad}: procesados={self.procesados}, insertados={self.insertados}, "
            f"duplicados={self.duplicados}, rechazados={self.rechazados}"
        )
