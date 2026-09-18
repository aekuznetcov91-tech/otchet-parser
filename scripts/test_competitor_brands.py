import sys
import pandas as pd

sys.path.append('.')
from scripts.build_avtogermes_analysis import df

df_cfo = df[df['is_cfo']]

print("=== ПРОДАЖИ ФЕДЕРАЛЬНЫХ ПАРТНЕРОВ ПО БРЕНДАМ В ЦФО (СУММА 3 МЕС) ===")
gk_brands = df_cfo.groupby(['gk', 'brand']).size().unstack().fillna(0).astype(int)
print(gk_brands.loc[['АвтоГЕРМЕС', 'РОЛЬФ', 'АВТОМИР', 'КОРС', 'МАЖОР', 'АГАТ']].to_string())

