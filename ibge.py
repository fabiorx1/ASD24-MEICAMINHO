import pandas as pd, openpyxl, pickle

CENSO_PATH = 'docs/populacao-2024.xls'

def get_populacao(cidade: str) -> pd.DataFrame:
    cidade, uf = cidade.split(' - ')
    df = pd.read_excel(CENSO_PATH, 'MUNICÍPIOS', header=1)
    df = df[df['UF'] == uf]
    line = df[df[df.columns[3]] == cidade].reset_index(drop=True)
    if len(line) > 0: return line[df.columns[-2]][0]
    return 0


nomes_estados = {
    'AC': 'Acre',
    'AL': 'Alagoas',
    'AP': 'Amapá',
    'AM': 'Amazonas',
    'BA': 'Bahia',
    'CE': 'Ceará',
    'DF': 'Distrito Federal',
    'ES': 'Espírito Santo',
    'GO': 'Goiás',
    'MA': 'Maranhão',
    'MT': 'Mato Grosso',
    'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais',
    'PA': 'Pará',
    'PB': 'Paraíba',
    'PR': 'Paraná',
    'PE': 'Pernambuco',
    'PI': 'Piauí',
    'RJ': 'Rio de Janeiro',
    'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul',
    'RO': 'Rondônia',
    'RR': 'Roraima',
    'SC': 'Santa Catarina',
    'SP': 'São Paulo',
    'SE': 'Sergipe',
    'TO': 'Tocantins'
}

macro_regioes = {
    'RO': 'Norte',
    'AC': 'Norte',
    'AM': 'Norte',
    'RR': 'Norte',
    'PA': 'Norte',
    'AP': 'Norte',
    'TO': 'Norte',
    'MA': 'Nordeste',
    'PI': 'Nordeste',
    'CE': 'Nordeste',
    'RN': 'Nordeste',
    'PB': 'Nordeste',
    'PE': 'Nordeste',
    'AL': 'Nordeste',
    'SE': 'Nordeste',
    'BA': 'Nordeste',
    'MG': 'Sudeste',
    'ES': 'Sudeste',
    'RJ': 'Sudeste',
    'SP': 'Sudeste',
    'PR': 'Sul',
    'SC': 'Sul',
    'RS': 'Sul',
    'MS': 'Centro-Oeste',
    'MT': 'Centro-Oeste',
    'GO': 'Centro-Oeste',
    'DF': 'Centro-Oeste'
}