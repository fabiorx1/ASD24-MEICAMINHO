#  MEI CAMINHO © 2024 by Fabio Augusto Ramalho, Matheus de Sousa Franco, Sofia Fernandes Cerqueira is licensed under CC BY-NC-SA 4.0 

import pandas as pd, openpyxl, pickle, re

CEMPRE1_FPATH = 'docs/cempre-cnae-municipios.xlsx'
CEMPRE2_FPATH = 'docs/mortalidade-2021.xlsx'
UFS_FPATH = 'static/estados.pickle'
DIVS_FPATH = 'static/divisoes.pickle'

def get_ufs():
    try:
        with open(UFS_FPATH, 'rb') as pickle_file:
            ufs = pickle.load(pickle_file)
    except:
        workbook = openpyxl.load_workbook(CEMPRE1_FPATH, data_only=True)
        ufs = workbook.sheetnames
        with open(UFS_FPATH, 'wb') as pickle_file:
            pickle.dump(ufs, pickle_file)
    finally: return ufs

def get_cities(uf: str):
    cidades_fpath = f'static/cidades-{uf}.pickle'
    try:
        with open(cidades_fpath, 'rb') as pickle_file:
            cidades = pickle.load(pickle_file)
    except:
        df = get_dataframe_by_uf(uf)
        cidades = df[df.columns[0]].unique()
        with open(cidades_fpath, 'wb') as pickle_file:
            pickle.dump(cidades, pickle_file)
    finally: return cidades

def get_divisoes():
    try:
        with open(DIVS_FPATH, 'rb') as pickle_file:
            divisoes = pickle.load(pickle_file)
    except:
        uf = get_ufs()[10]
        df = get_dataframe_by_uf(uf)
        is_not_digit = lambda x: not x.isdigit()
        cidade = df[df.columns[0]].values[0]
        df = df[df[df.columns[0]] == cidade]
        df = df[df[df.columns[1]].astype(str).apply(is_not_digit)]
        df = df.drop(df.index[0])
        divisoes = df[df.columns[2]].unique()
        with open(DIVS_FPATH, 'wb') as pickle_file:
            pickle.dump(divisoes, pickle_file)
    finally: return divisoes

def get_cnaes(divisao: str):
    cnaes_fpath = f'static/cnaes-{divisao}.pickle'
    try:
        with open(cnaes_fpath, 'rb') as pickle_file:
            cnaes = pickle.load(pickle_file)
    except:
        uf = get_ufs()[10]
        df = get_dataframe_by_uf(uf)
        cidade = df[df.columns[0]].values[0]
        df = df[df[df.columns[0]] == cidade]
        df = df.drop(df.index[0])
        cnaes_idxs = []
        for j, v1 in enumerate(df[df.columns[2]]):
            if v1 == divisao:
                for i, v2 in enumerate(df[df.columns[1]][j+1:]):
                    if not v2.isdigit(): break
                    cnaes_idxs.append(df.index[j+i+1])
                break
        cnaes = df[df.columns[2]][cnaes_idxs]
        with open(cnaes_fpath, 'wb') as pickle_file:
            pickle.dump(cnaes, pickle_file)
    finally: return cnaes

def get_dataframe_by_uf(uf: str) -> pd.DataFrame:
    df = pd.read_excel(CEMPRE1_FPATH, uf, header=3)
    df = df.rename(columns={c: c.replace('\n', ' ') for c in df.columns})
    df = df.rename(columns={c: c.replace('unidades locais', 'empresas') for c in df.columns})
    for e in ['(1)', '(2)', '(3)']:
        df = df.rename(columns={c: c.replace(e, '') for c in df.columns})
    cols = df.columns
    df = df.rename(
        columns={cols[4]: cols[4] + ' ' + df[cols[4]][0],
                 cols[5]: cols[4] + ' ' + df[cols[5]][0]})
    df = df.drop([df.index[0], *df.index[-6:]])
    df = df.replace('X', 1)
    df = df.replace('-', 0)
    return df

def get_tendencia(setor: str, regiao: str):
    df = pd.read_excel(CEMPRE2_FPATH, header=5)
    df = df[df[df.columns[0]].apply(lambda s: str(s).find(regiao) >= 0)]
    df = df[df[df.columns[1]].apply(lambda v: v[2:].find(setor) >= 0)]
    return (df[df.columns[a]][df.index[0]] - df[df.columns[b]][df.index[0]]
            for a, b in [(3, 5), (4, 6), (8, 10), (9, 11)])

def initialize(ufs: list = None):
    if not ufs: ufs = get_ufs()
    for uf in ufs: get_cities(uf)