import sys
import pandas as pd
from collections import Counter

sys.path.append('.')
from scripts.build_avtogermes_analysis import df

df_cfo = df[df['is_cfo']]

print("=== РЫНОК БРЕНДОВ В ЦФО (ПРОДАЖИ ПО МЕСЯЦАМ) ===")
b_cfo = df_cfo.groupby(['brand', 'month']).size().unstack().fillna(0).astype(int)
b_cfo['Total_CFO_3M'] = b_cfo.sum(axis=1)
b_cfo = b_cfo.sort_values(by='Total_CFO_3M', ascending=False)
print(b_cfo.to_string())

print("\n=== ПРОДАЖИ АВТОГЕРМЕСА ПО БРЕНДАМ В ЦФО ===")
ag_cfo = df_cfo[df_cfo['gk'] == 'АвтоГЕРМЕС']
b_ag = ag_cfo.groupby(['brand', 'month']).size().unstack().fillna(0).astype(int)
b_ag['Total_AG_3M'] = b_ag.sum(axis=1)
b_ag = b_ag.sort_values(by='Total_AG_3M', ascending=False)
print(b_ag.to_string())

print("\n=== ДОЛИ АВТОГЕРМЕСА В БРЕНДАХ ЦФО ===")
shares = []
for b in b_cfo.index:
    ag_3m = b_ag.loc[b, 'Total_AG_3M'] if b in b_ag.index else 0
    cfo_3m = b_cfo.loc[b, 'Total_CFO_3M']
    sh_3m = (ag_3m / cfo_3m * 100) if cfo_3m > 0 else 0
    
    ag_m1 = b_ag.loc[b, '2026-06'] if (b in b_ag.index and '2026-06' in b_ag.columns) else 0
    cfo_m1 = b_cfo.loc[b, '2026-06'] if '2026-06' in b_cfo.columns else 0
    sh_m1 = (ag_m1 / cfo_m1 * 100) if cfo_m1 > 0 else 0

    ag_m2 = b_ag.loc[b, '2026-07'] if (b in b_ag.index and '2026-07' in b_ag.columns) else 0
    cfo_m2 = b_cfo.loc[b, '2026-07'] if '2026-07' in b_cfo.columns else 0
    sh_m2 = (ag_m2 / cfo_m2 * 100) if cfo_m2 > 0 else 0

    ag_m3 = b_ag.loc[b, '2026-08'] if (b in b_ag.index and '2026-08' in b_ag.columns) else 0
    cfo_m3 = b_cfo.loc[b, '2026-08'] if '2026-08' in b_cfo.columns else 0
    sh_m3 = (ag_m3 / cfo_m3 * 100) if cfo_m3 > 0 else 0
    
    shares.append({
        'brand': b,
        'AG_3M': ag_3m,
        'CFO_3M': cfo_3m,
        'Share_3M_%': round(sh_3m, 2),
        'AG_Jun': ag_m1, 'CFO_Jun': cfo_m1, 'Share_Jun_%': round(sh_m1, 2),
        'AG_Jul': ag_m2, 'CFO_Jul': cfo_m2, 'Share_Jul_%': round(sh_m2, 2),
        'AG_Aug': ag_m3, 'CFO_Aug': cfo_m3, 'Share_Aug_%': round(sh_m3, 2)
    })

df_shares = pd.DataFrame(shares)
print(df_shares.head(15).to_string(index=False))

