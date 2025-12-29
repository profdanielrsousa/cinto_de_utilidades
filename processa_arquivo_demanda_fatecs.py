#  PROCESSA ARQUIVO DEMANDA FATECS (PÓS PROCESSAMENTO DE busca_demanda_vestibular_fatec.py)
#  ESTE PROGRAMA FAZ O PÓS PROCESSAMENTO DO ARQUIVO todas_fatecs_demanda.csv, NORMALIZANDO O NOME DAS UNIDADES.
#  NO FINAL, ELE GERA UM ARQUIVO CSV COM OS DADOS NORMALIZADOS (todas_fatecs_demanda_normalizado.csv).
#  DANIEL RODRIGUES DE SOUSA 27/12/2025

import pandas as pd

# Configuração de arquivos
INPUT_CSV = "todas_fatecs_demanda.csv"                       # arquivo original com os dados
                                                             # gerado pelo busca_demanda_vestibular_fatec.py
OUTPUT_NORMALIZED = "todas_fatecs_demanda_normalizado.csv"   # saída final
DICT_TEMPLATE = "dicionario.csv"                             # gerado com valores únicos (útil para a criação do dicionário)
DICT_CSV = "dicionario_editado.csv"                          # seu dicionário editado (um alias por linha)

# Normalização mínima: só espaços (colapsa internos + strip)
def normalize_space(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    return " ".join(s.split()).strip()

# Lê dicionário: 2 colunas (aliases, canonical), sem separadores no aliases
def build_alias_mapping(dict_csv_path: str):
    """
    Espera CSV com:
      - aliases: um único valor por linha (sem separadores) - DE
      - canonical: alvo canônico - PARA
    Retorna: {ALIAS_NORMALIZADO_EM_UPPER: CANONICAL_NORMALIZADO}
    """
    dic = pd.read_csv(dict_csv_path, encoding="utf-8")
    dic.columns = [c.strip().lower() for c in dic.columns]
    if "aliases" not in dic.columns:
        dic.rename(columns={dic.columns[0]: "aliases"}, inplace=True)
    if "canonical" not in dic.columns:
        dic.rename(columns={dic.columns[1]: "canonical"}, inplace=True)

    dmap = {}
    for _, row in dic.iterrows():
        alias = normalize_space(str(row.get("aliases", "")))
        canonical = normalize_space(str(row.get("canonical", "")))
        key = alias.upper()
        if key:
            dmap[key] = canonical
    return dmap

# Normaliza e aplica o mapa para um campo específico
def normalize_column(df: pd.DataFrame, column_name: str, dmap: dict) -> pd.DataFrame:
    if column_name not in df.columns:
        raise KeyError(f"Coluna '{column_name}' não encontrada no CSV.")
    out = df.copy()
    norm_before = out[column_name].astype(str).apply(normalize_space)
    keys_upper = norm_before.str.upper()
    canon = keys_upper.map(lambda k: dmap.get(k, None))
    out[column_name] = norm_before
    mask = canon.notna()
    out.loc[mask, column_name] = canon[mask].values
    return out

# Fluxo principal
df = pd.read_csv(INPUT_CSV, encoding="utf-8")

# Gera template com valores únicos de Unidade e Período (já normalizadas)
templates = []

# Unidade
if "Unidade" in df.columns:
    uniq_un = (
        pd.DataFrame({"Unidade": df["Unidade"].astype(str)})
        .assign(aliases=lambda d: d["Unidade"].apply(normalize_space))
        .drop_duplicates(subset=["aliases"])
    )[["aliases"]]
    uniq_un["canonical"] = uniq_un["aliases"]
    templates.append(uniq_un[["aliases", "canonical"]])

# Período
if "Período" in df.columns:
    uniq_pe = (
        pd.DataFrame({"Período": df["Período"].astype(str)})
        .assign(aliases=lambda d: d["Período"].apply(normalize_space))
        .drop_duplicates(subset=["aliases"])
    )[["aliases"]]
    uniq_pe["canonical"] = uniq_pe["aliases"]
    templates.append(uniq_pe[["aliases", "canonical"]])

# Concatena e salva template único
template_df = pd.concat(templates, ignore_index=True)
template_df.to_csv(DICT_TEMPLATE, index=False, encoding="utf-8")

# Carrega seu dicionário (ou use o template)
dmap = build_alias_mapping(DICT_CSV)

# Aplica normalização e mapeamento nas duas colunas
out = df.copy()
out = normalize_column(out, "Unidade", dmap)
out = normalize_column(out, "Período", dmap)

# Salva saída final
out.to_csv(OUTPUT_NORMALIZED, index=False, encoding="utf-8")

print({
    "linhas_no_arquivo": len(df),
    "linhas_no_dicionario": len(template_df),
    "arquivo_dicionario": DICT_TEMPLATE,
    "arquivo_gerado": OUTPUT_NORMALIZED
})
