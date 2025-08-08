#  BUSCA EDITAL CESU
#  ESTE PROGRAMA LÊ OS DADOS DO SITE DA CESU (https://cesu.cps.sp.gov.br/editaisabertos/), POSSIBILITANDO A FILTRAGEM DOS DADOS.
#  NO FINAL, ELE GERA UM ARQUIVO EM PDF COM OS EDITAIS DE INTERESSE (editais.pdf).
#  DANIEL RODRIGUES DE SOUSA 19/03/2025

import pandas as pd
import requests
import csv
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Fonte utilizada
FONT_PATH = "DejaVuSans.ttf"

# URL da planilha do Google Sheets e arquivo .csv salvo
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSPxryxjiyOz0bW5AIaB45RrgU-mp9O-bCFWWa9NIsu8f-80FZEz-dUKIR6fZ9qeGBW83clfV3-L_zF/pub?gid=0&single=true&output=csv"
CSV_PATH = "editais_cesu.csv"

# Vetores de dados que vão limitar a impressão dos editais. Filtros de busca (vazios = sem filtro)
# obs: se o vetor estiver vazio, imprime todos os dados da coluna 

fatec_vetor = [] # Exemplo: fatec_vetor = ["Tatuí", "Baixada Santista"]
curso_vetor = [] # Exemplo: curso_vetor = ["Gestão da Tecnologia da Informação", "Processos Gerenciais"]           
disciplina_vetor = [] # Exemplo: disciplina_vetor = ["PROJETOS DE TECNOLOGIA DA INFORMAÇÃO II", "Teoria das Organizações"]
area_disciplina_vetor = [] # Exemplo: area_disciplina_vetor = ["Ciência da computação", "Administração e negócios"]
determinado_vetor = [] # Exemplo: determinado_vetor = ["Determinado", "Indeterminado"]
periodo_aula_vetor = [] # Exemplo: periodo_aula_vetor = ["Noturno", "Vespertino"]

# Baixar .csv
print("Baixando arquivo CSV...")
response = requests.get(CSV_URL)
response.raise_for_status()
with open(CSV_PATH, 'wb') as f:
    f.write(response.content)
print("CSV baixado com sucesso:", CSV_PATH)

# Ler .csv com Pandas
df = pd.read_csv(CSV_PATH, sep=',', encoding='utf-8-sig')

# Padronizar nomes das colunas (ajuste conforme necessário)
df.columns = [
    "Edital No", "Fatec", "Curso", "Disciplina", "Área da disciplina", 
    "Determinado ou indeterminado", "Período", "Data abertura",
    "Data limite","Edital", "Ficha", "Tabela"
]

# Convertendo colunas de data
df["Data limite"] = pd.to_datetime(df["Data limite"], format="%d/%m/%Y", errors='coerce')
df["Data abertura"] = pd.to_datetime(df["Data abertura"], format="%d/%m/%Y", errors='coerce')

# Apenas editais válidos
hoje = pd.to_datetime(datetime.now().date())
df = df[df["Data limite"] >= hoje]

# Aplicação do filtro
def aplicar_filtro(coluna, vetor):
    return df[coluna].isin(vetor) if vetor else pd.Series([True] * len(df))

filtros = (
    aplicar_filtro("Fatec", fatec_vetor) &
    aplicar_filtro("Curso", curso_vetor) &
    aplicar_filtro("Disciplina", disciplina_vetor) &
    aplicar_filtro("Área da disciplina", area_disciplina_vetor) &
    aplicar_filtro("Determinado ou indeterminado", determinado_vetor) &
    aplicar_filtro("Período", periodo_aula_vetor)
)

df_filtrado = df[filtros]

if df_filtrado.empty:
    print("Nenhum edital encontrado com os critérios especificados.")
    exit(0)

# Gerando o PDF com os editais encontrados, caso existam
pdf = FPDF()
pdf.add_page()
pdf.add_font("DejaVu", "", FONT_PATH)
pdf.set_font("DejaVu", size=12)

# Começo do "bloco"
pdf.set_fill_color(240, 240, 240)  # cinza claro
pdf.set_draw_color(200, 200, 200)

# Mudando a cor do texto para azul antes de adicionar o hiperlink
pdf.set_text_color(0, 0, 255)

# Cabeçalho do bloco
pdf.cell(0, 8, "https://cesu.cps.sp.gov.br/editaisabertos/", link='https://cesu.cps.sp.gov.br/editaisabertos/',
         new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
pdf.cell(0, 8, "Tabelas de áreas, disciplinas e especificidades",
         link='https://cesu.cps.sp.gov.br/diretrizes-para-alteracao-de-carga-horaria-docente-concurso-publico-pss/',
         new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

# Resetando a cor do texto para preto
pdf.set_text_color(0, 0, 0)

# Formatando a data e hora no formato desejado
pdf.cell(0, 8, f"Data: {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

for _, edital in df_filtrado.iterrows():
    
    # Estimar altura e quebrar página se necessário
    altura_bloco = 70  # ajuste conforme necessário
    if pdf.get_y() + altura_bloco > pdf.page_break_trigger:
        pdf.add_page()

    # Começo do "bloco"
    pdf.set_fill_color(240, 240, 240)  # cinza claro
    pdf.set_draw_color(200, 200, 200)
    pdf.cell(0, 6, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Cabeçalho do bloco
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Edital Nº {edital['Edital No']} - Fatec {edital['Fatec']}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

    # Linha 1 e 2
    pdf.cell(0, 6, f"Curso: {edital['Curso']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f"Disciplina: {edital['Disciplina']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Linha 3
    pdf.cell(100, 6, f"Período: {edital['Período']}", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(0, 6, f"Tipo: {edital['Determinado ou indeterminado']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Tratamento seguro para datas
    data_abertura = edital['Data abertura'].strftime('%d/%m/%Y') if pd.notnull(edital['Data abertura']) else "---"
    data_limite = edital['Data limite'].strftime('%d/%m/%Y') if pd.notnull(edital['Data limite']) else "---"

    # Linha 4
    pdf.cell(100, 6, f"Abertura: {data_abertura}", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(0, 6, f"Encerramento: {data_limite}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Área e links
    pdf.multi_cell(0, 6, f"Área(s): {edital['Área da disciplina']}")

    pdf.set_text_color(0, 0, 255)
    pdf.cell(0, 0, text="", new_x=XPos.LMARGIN, new_y=YPos.TOP)
    pdf.cell(0, 6, "Link do Edital", link=str(edital['Edital']), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, "Ficha de Interesse", link=str(edital['Ficha']), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, "Tabela de Pontuação", link=str(edital['Tabela']), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    
    # Espaço inferior
    pdf.cell(0, 4, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

pdf.output("editais.pdf")
print("✅ Arquivo 'editais.pdf' gerado com sucesso!")
