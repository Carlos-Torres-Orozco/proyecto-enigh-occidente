import pandas as pd
h = pd.read_csv('data/processed/hogares_2016_2024.csv', dtype={'folioviv': str})
t = h.assign(w=h['factor'] * h['D_jefe_o_conyuge_autoads']).groupby(['estado', 'anio'])[['w', 'factor']].sum()
print((100 * t['w'] / t['factor']).unstack().round(1))