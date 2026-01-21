import requests
import pandas as pd
import sys

state = ''
level = '' # to be read

# States listed on the IJ Honra Estadual page
STATES = [
    "AC", "AL", "AM", "BA", "CE", "DF", "GO", "MA", "MG",
    "MS", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO",
    "RS", "SC", "SE", "SP",
]


all_dfs = []

level = sys.argv[1]
OUTPUT_CSV = f"honra_estadual_{level}_2025.csv"

if level not in ('ij','i1','i2'):
    print(f"usage: {sys.argv[0]} level",file=sys.stderr)
    
for uf in STATES:
    state = uf
    url = f"https://olimpiada.ic.unicamp.br/resultados/honra_estadual/{level}/{state}_{level}/"
    print(f"Baixando {uf} -> {url}")

    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"  [ERRO] {uf}: status {resp.status_code}, pulando.")
        continue

    # pandas tenta encontrar todas as tabelas na página
    try:
        tables = pd.read_html(resp.text)
    except ValueError:
        print(f"  [ERRO] {uf}: nenhuma tabela encontrada, pulando.")
        continue

    if not tables:
        print(f"  [ERRO] {uf}: nenhuma tabela encontrada, pulando.")
        continue

    df = tables[0]  # primeira tabela da página

    # Em geral deve ter 5 colunas: Classif., Nota, Nome, Escola, Cidade.
    # Para garantir, cortamos para as 5 primeiras e renomeamos.
    if df.shape[1] >= 5:
        df = df.iloc[:, :5]
        df.columns = ["classif", "nota", "nome", "escola", "cidade"]
    else:
        print(f"  [AVISO] {uf}: menos de 5 colunas, mantendo como está.")
    
    # adiciona UF e URL de origem (útil para conferência)
    df["uf"] = uf
    df["origem"] = url

    all_dfs.append(df)

if not all_dfs:
    print("Nenhum dado coletado. Verifique o script ou as páginas.")
else:
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nOK! CSV gerado em: {OUTPUT_CSV}")
    print(f"Total de linhas: {len(final_df)}")
