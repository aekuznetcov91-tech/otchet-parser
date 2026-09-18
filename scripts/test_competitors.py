import sys
import pandas as pd
from collections import Counter

sys.path.append('.')
from scripts.build_avtogermes_analysis import df

df_cfo = df[df['is_cfo']]

print("=== ФЕДЕРАЛЬНЫЕ ПАРТНЕРЫ В ЦФО (ПРОДАЖИ ПО МЕСЯЦАМ) ===")
gk_summary = df_cfo.groupby(['gk', 'month']).size().unstack().fillna(0).astype(int)
gk_summary['Total_3M'] = gk_summary.sum(axis=1)
gk_summary = gk_summary.sort_values(by='Total_3M', ascending=False)
print(gk_summary.to_string())

print("\nДоли в ЦФО за 3 месяца:")
cfo_total = len(df_cfo)
for gk, row in gk_summary.iterrows():
    sh = row['Total_3M'] / cfo_total * 100
    print(f"  {gk}: {row['Total_3M']} шт. ({sh:.2f}%)")

