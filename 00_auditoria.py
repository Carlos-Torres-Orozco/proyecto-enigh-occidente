import re
import sys
import difflib
from pathlib import Path
import pandas as pd

BASE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
ESTADOS = {'06': 'Colima', '14': 'Jalisco', '16': 'Michoacán', '18': 'Nayarit'}

COLS = {
    'concentradohogar': [
        'folioviv', 'foliohog', 'ubica_geo', 'factor', 'upm', 'est_dis',
        'clase_hog', 'tot_integ', 'hombres', 'mujeres', 'menores', 'mayores', 'p12_64', 'p65mas',
        'est_socio', 'ing_cor', 'educa_jefe', 'sexo_jefe', 'edad_jefe', 'tam_loc',
        'gasto_mon', 'salud', 'educacion', 'esparci', 'alimentos', 'transporte', 'vesti_calz',
        'adqui_vehi', 'paq_turist', 'educa_espa',
    ],
    'poblacion': [
        'folioviv', 'foliohog', 'numren', 'parentesco', 'pareja_hog',
        'sexo', 'edad', 'entidad', 'hablaind', 'etnia', 'nivelaprob', 'gradoaprob',
    ],
}
CATALOGOS = {
    'concentradohogar': ['clase_hog', 'educa_jefe', 'est_socio', 'tam_loc', 'sexo_jefe'],
    'poblacion': ['parentesco', 'nivelaprob', 'hablaind', 'etnia', 'sexo'],
}


def leer_encabezado(ruta):
    for enc in ('utf-8-sig', 'latin-1'):
        try:
            return pd.read_csv(ruta, nrows=0, encoding=enc).columns.str.strip().tolist(), enc
        except UnicodeDecodeError:
            continue
    raise ValueError(f'No pude leer {ruta}')


def anio_de(ruta):
    m = re.findall(r'(20\d{2})', ruta.name) or re.findall(r'(20\d{2})', str(ruta))
    return int(m[-1]) if m else None


def localizar():
    hallados = {}
    for p in BASE.rglob('*.csv'):
        s = str(p).lower()
        if 'diccionario' in s or 'estacional' in s or 'auditoria' in p.name.lower():
            continue
        for tabla in COLS:
            if tabla in p.name.lower():
                anio = anio_de(p)
                hallados.setdefault((tabla, anio), p)
    return hallados


archivos = localizar()
if not archivos:
    sys.exit(f'No encontré CSV de datos bajo {BASE}')
anios = sorted({a for _, a in archivos})


enc_cols = {k: leer_encabezado(r)[0] for k, r in archivos.items()}
filas = []
for tabla, lista in COLS.items():
    for var in lista:
        fila = {'tabla': tabla, 'variable': var}
        for a in anios:
            cols = enc_cols.get((tabla, a))
            if cols is None:
                fila[a] = 'sin archivo'
            elif var in cols:
                fila[a] = 'OK'
            else:
                parecidas = difflib.get_close_matches(var, cols, n=3, cutoff=0.75)
                fila[a] = 'FALTA' + (f' (¿{", ".join(parecidas)}?)' if parecidas else '')
        filas.append(fila)
aud_cols = pd.DataFrame(filas)
aud_cols.to_csv('auditoria_columnas.csv', index=False, encoding='utf-8-sig')
pd.set_option('display.width', 250, 'display.max_colwidth', 60, 'display.max_rows', 200)


filas = []
for tabla, vars_ in CATALOGOS.items():
    for var in vars_:
        fila = {'tabla': tabla, 'variable': var}
        for a in anios:
            ruta = archivos.get((tabla, a))
            if ruta is None or var not in enc_cols[(tabla, a)]:
                fila[a] = 'n/d'
                continue
            enc = leer_encabezado(ruta)[1]
            crudo = {c.strip(): c for c in pd.read_csv(ruta, nrows=0, encoding=enc).columns}[var]
            s = pd.read_csv(ruta, usecols=[crudo], dtype=str, encoding=enc)[crudo].str.strip()
            vals = sorted(s.dropna().unique(), key=lambda x: (len(x), x))
            fila[a] = ' '.join(vals) if len(vals) <= 40 else f'{len(vals)} valores distintos'
        filas.append(fila)
aud_cat = pd.DataFrame(filas)
aud_cat.to_csv('auditoria_catalogos.csv', index=False, encoding='utf-8-sig')


filas = []
for a in anios:
    ruta = archivos.get(('concentradohogar', a))
    if ruta is None:
        continue
    cols = enc_cols[('concentradohogar', a)]
    if 'ubica_geo' not in cols or 'factor' not in cols:
        continue
    enc = leer_encabezado(ruta)[1]
    mapa = {c.strip(): c for c in pd.read_csv(ruta, nrows=0, encoding=enc).columns}
    d = pd.read_csv(ruta, usecols=[mapa['ubica_geo'], mapa['factor']], dtype=str, encoding=enc)
    d.columns = d.columns.str.strip()
    d['factor'] = pd.to_numeric(d['factor'], errors='coerce')
    d['ent'] = d['ubica_geo'].str.zfill(5).str[:2]
    d = d[d['ent'].isin(ESTADOS)]
    for ent, g in d.groupby('ent'):
        filas.append({'anio': a, 'estado': ESTADOS[ent],
                      'hogares_muestra': len(g), 'hogares_expandidos': round(g['factor'].sum())})
aud_m = pd.DataFrame(filas)
aud_m.to_csv('auditoria_muestra.csv', index=False, encoding='utf-8-sig')
