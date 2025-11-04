# api/utils.py
"""
Funções utilitárias para carregar e consultar o dataset em memória.
"""

import pandas as pd
from api.config import settings

# carrega o CSV em um DataFrame global (pode ser substituído por DB no futuro)
def load_data(path: str | None = None) -> pd.DataFrame:
    path = path or settings.DATA_PATH
    df = pd.read_csv(path)
    # assegura coluna id
    if "id" not in df.columns:
        df.insert(0, "id", range(1, len(df) + 1))
    # cria coluna numérica de preço, se possível
    def price_to_float(x):
        try:
            return float(str(x).replace("£", "").strip())
        except:
            return None
    df["price_num"] = df["price"].apply(price_to_float)
    return df