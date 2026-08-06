import pandas as pd


def generar_dim_clasificacion():
    valores = ['Positiva', 'Neutra', 'Negativa']
    return pd.DataFrame({'Clasificacion': valores})
