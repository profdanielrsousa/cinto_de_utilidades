#  BUSCA EDITAL CESU
#  ESTE PROGRAMA LÊ OS DADOS DO SITE DA CESU (https://cgesg.cps.sp.gov.br/editais-cgesg/), POSSIBILITANDO A FILTRAGEM DOS DADOS.
#  NO FINAL, ELE GERA UM ARQUIVO EM PDF COM OS EDITAIS DE INTERESSE (editais.pdf).
#  DANIEL RODRIGUES DE SOUSA 19/03/2025

import os
import time
import tempfile
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ======================================================
# DOWNLOAD DO CSV DA CGESG (COM PASTA TEMPORÁRIA)
# ======================================================
def baixar_csv_cgesg():
    URL = "https://cgesg.cps.sp.gov.br/editais-cgesg/"

    temp_dir = tempfile.TemporaryDirectory()

    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": temp_dir.name,
        "download.prompt_for_download": False,
        "directory_upgrade": True
    })

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(URL)
        time.sleep(5)  # Aguarda JS

        botao = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[normalize-space()='Download CSV (Excell)']")
            )
        )

        driver.execute_script("arguments[0].click();", botao)

        timeout = time.time() + 30
        while time.time() < timeout:
            arquivos = [
                f for f in os.listdir(temp_dir.name)
                if f.endswith(".csv") and not f.endswith(".crdownload")
            ]
            if arquivos:
                return os.path.join(temp_dir.name, arquivos[0]), temp_dir

            time.sleep(1)

        raise RuntimeError("CSV não foi baixado.")

    except Exception:
        temp_dir.cleanup()
        raise

    finally:
        driver.quit()

# ======================================================
# FILTRO FLEXÍVEL (SUPORTA CAMPOS MULTI-VALOR)
# ======================================================
def aplicar_filtro(df, coluna, vetor):
    if not vetor:
        return pd.Series([True] * len(df))

    def corresponde(celula):
        sub = [v.strip().lower() for v in str(celula).split(',') if v.strip()]
        return any(v.lower().strip() in sub for v in vetor)

    return df[coluna].apply(corresponde)

# ======================================================
# PROGRAMA PRINCIPAL
# ======================================================
FONT_PATH = "DejaVuSans.ttf"

print("📥 Baixando CSV da CGESG...")
csv_path, temp_dir = baixar_csv_cgesg()
print("✅ CSV baixado.")

try:
    # Ler .csv com Pandas
    df = pd.read_csv(
        csv_path,
        sep=";",
        encoding="utf-8-sig",
        on_bad_lines="skip"
    )

    # Padronizar nomes das colunas (ajuste conforme necessário)
    df.columns = [
        "Edital No", "Fatec", "Curso", "Disciplina", "Área da disciplina",
        "Determinado ou indeterminado", "Período", "Data abertura",
        "Data limite", "Edital", "Ficha", "Tabela"
    ]
       
    # Extrai apenas a primeira data válida do texto
    for coluna in ["Data limite", "Data abertura"]:
        df[coluna] = (
            df[coluna]
            .astype(str)
            .str.extract(r"(\d{2}/\d{2}/\d{4})", expand=False)
        )

        df[coluna] = pd.to_datetime(
            df[coluna],
            format="%d/%m/%Y",
            errors="coerce"
        )

    # Apenas editais válidos
    hoje = pd.to_datetime(datetime.now().date())
    df = df[df["Data limite"] >= hoje]

    # ======================
    # FILTROS (OPCIONAIS)
    # ======================
    
    # Vetores de dados que vão limitar a impressão dos editais. Filtros de busca (vazios = sem filtro)
    # obs: se o vetor estiver vazio, imprime todos os dados da coluna 

    fatec_vetor = [] # Exemplo: fatec_vetor = ["Tatuí", "Baixada Santista"]
    curso_vetor = [] # Exemplo: curso_vetor = ["Gestão da Tecnologia da Informação", "Processos Gerenciais"]           
    disciplina_vetor = [] # Exemplo: disciplina_vetor = ["PROJETOS DE TECNOLOGIA DA INFORMAÇÃO II", "Teoria das Organizações"]
    area_disciplina_vetor = [] # Exemplo: area_disciplina_vetor = ["Ciência da computação", "Administração e negócios"]
    determinado_vetor = [] # Exemplo: determinado_vetor = ["Determinado", "Indeterminado"]
    periodo_aula_vetor = [] # Exemplo: periodo_aula_vetor = ["Noturno", "Vespertino"]    
        
    filtros = (
        aplicar_filtro(df, "Fatec", fatec_vetor) &
        aplicar_filtro(df, "Curso", curso_vetor) &
        aplicar_filtro(df, "Disciplina", disciplina_vetor) &
        aplicar_filtro(df, "Área da disciplina", area_disciplina_vetor) &
        aplicar_filtro(df, "Determinado ou indeterminado", determinado_vetor) &
        aplicar_filtro(df, "Período", periodo_aula_vetor)
    )

    df_filtrado = df[filtros]

    if df_filtrado.empty:
        print("Nenhum edital encontrado com os critérios especificados.")
        flag_edital = False
    else:
        flag_edital = True

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
    pdf.cell(0, 8, "https://cgesg.cps.sp.gov.br/editais-cgesg/", link='https://cgesg.cps.sp.gov.br/editais-cgesg/',
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
    pdf.cell(0, 8, "Tabelas de áreas, disciplinas e especificidades",
             link='https://cgesg.cps.sp.gov.br/diretrizes-para-alteracao-de-carga-horaria-docente-concurso-publico-pss/',
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

    # Resetando a cor do texto para preto
    pdf.set_text_color(0, 0, 0)

    # Formatando a data e hora no formato desejado
    pdf.cell(0, 8, f"Data: {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

    if flag_edital == True:
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

    else:
        
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
        pdf.cell(0, 8, f"Nenhum edital encontrado com os critérios especificados.",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

    pdf.output("editais.pdf")
    print("✅ Arquivo 'editais.pdf' gerado com sucesso!")

finally:
    # Limpeza automática da pasta temporária
    temp_dir.cleanup()
