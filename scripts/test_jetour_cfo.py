import sys
import pandas as pd
from collections import Counter

sys.path.append('.')
from scripts.build_avtogermes_analysis import df

df_cfo = df[df['is_cfo']]

print("=== РЫНОК JETOUR В ЦФО ===")
jetour_cfo = df_cfo[df_cfo['brand'] == 'JETOUR']
print(f"Всего продаж JETOUR в ЦФО за 3 мес: {len(jetour_cfo)}")
j_month = jetour_cfo['month'].value_counts().sort_index()
print("JETOUR в ЦФО по месяцам:\n", j_month)

ag_jetour = jetour_cfo[jetour_cfo['gk'] == 'АвтоГЕРМЕС']
print("\nАвтоГЕРМЕС JETOUR в ЦФО по месяцам:\n", ag_jetour['month'].value_counts().sort_index())
for m in ['2026-06', '2026-07', '2026-08']:
    m_tot = j_month.get(m, 0)
    m_ag = len(ag_jetour[ag_jetour['month'] == m])
    sh = (m_ag / m_tot * 100) if m_tot > 0 else 0
    print(f"  {m}: АвтоГЕРМЕС {m_ag} шт. из {m_tot} шт. ({sh:.2f}%)")

print("\n=== ТОП-20 ДИЛЕРОВ JETOUR В ЦФО ЗА ПОСЛЕДНИЕ 2 МЕСЯЦА (ИЮЛЬ + АВГУСТ) ===")
j2m = jetour_cfo[jetour_cfo['month'].isin(['2026-07', '2026-08'])]
print(f"Всего продаж JETOUR в ЦФО за Июль-Август: {len(j2m)}")

dealers = j2m.groupby(['company', 'month']).size().unstack().fillna(0).astype(int)
dealers['Total_2M'] = dealers.sum(axis=1)
dealers = dealers.sort_values(by='Total_2M', ascending=False)

print(dealers.head(25).to_string())

