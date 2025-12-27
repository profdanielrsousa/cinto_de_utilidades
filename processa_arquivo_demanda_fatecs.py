#  PROCESSA ARQUIVO DEMANDA FATECS (PÓS PROCESSAMENTO DE busca_demanda_vestibular_fatec.py)
#  ESTE PROGRAMA FAZ O PÓS PROCESSAMENTO DO ARQUIVO todas_fatecs_demanda.csv, NORMALIZANDO O NOME DAS UNIDADES.
#  NO FINAL, ELE GERA UM ARQUIVO CSV COM OS DADOS NORMALIZADOS (todas_fatecs_demanda_normalizado.csv).
#  DANIEL RODRIGUES DE SOUSA 27/12/2025

import pandas as pd

# Configuração de arquivos
INPUT_CSV = "todas_fatecs_demanda.csv"                       # arquivo original com os dados
                                                             # gerado pelo busca_demanda_vestibular_fatec.py
OUTPUT_NORMALIZED = "todas_fatecs_demanda_normalizado.csv"   # saída final
DICT_TEMPLATE = "dic_unidades_template.csv"                  # gerado com valores únicos (útil para a criação do dicionário)
DICT_CSV = "dic_unidades_template_edited.csv"                # seu dicionário editado (um alias por linha)

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

# Normaliza e aplica o mapa
def normalize_unidade(df: pd.DataFrame, dmap: dict) -> pd.DataFrame:
    if "Unidade" not in df.columns:
        raise KeyError("Coluna 'Unidade' não encontrada no CSV.")
    out = df.copy()

    # normalização básica de espaços
    norm_before = out["Unidade"].astype(str).apply(normalize_space)
    keys_upper = norm_before.str.upper()

    # aplica dicionário (se existir chave, troca pelo canonical)
    canon = keys_upper.map(lambda k: dmap.get(k, None))
    out["Unidade"] = norm_before
    mask = canon.notna()
    out.loc[mask, "Unidade"] = canon[mask].values
    return out

# Fluxo principal
df = pd.read_csv(INPUT_CSV, encoding="utf-8")

# Gera template com Unidades únicas (já normalizadas)
unique_unidades = (
    pd.DataFrame({"Unidade": df["Unidade"].astype(str)})
    .assign(Unidade_normalizada=lambda d: d["Unidade"].apply(normalize_space))
    .drop_duplicates(subset=["Unidade_normalizada"])
)
template = unique_unidades["Unidade_normalizada"].to_frame(name="aliases")
template["canonical"] = template["aliases"]  # por padrão, alias == canonical
template.to_csv(DICT_TEMPLATE, index=False)

# Carrega seu dicionário (ou use o template)
dmap = build_alias_mapping(DICT_CSV)

# Aplica normalização + mapeamento e salva
normalized_df = normalize_unidade(df, dmap)
normalized_df.to_csv(OUTPUT_NORMALIZED, index=False)

print({
    "linhas_no_arquivo": len(df),
    "unidades_unicas_no_template": len(template),
    "arquivo_gerado": OUTPUT_NORMALIZED
})