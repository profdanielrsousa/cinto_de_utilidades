#  BUSCA EDITAL CESU
#  ESTE PROGRAMA LÊ OS DADOS DO SITE DA CESU (https://cesu.cps.sp.gov.br/editaisabertos/), POSSIBILITANDO A FILTRAGEM DOS DADOS.
#  NO FINAL, ELE GERA UM ARQUIVO EM PDF COM OS EDITAIS DE INTERESSE (editais.pdf).
#  DANIEL RODRIGUES DE SOUSA 19/03/2025

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos

FONT_PATH = "DejaVuSans.ttf"

def safe(texto):
    return texto if texto else ''

# URL da planilha do Google Sheets
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSPxryxjiyOz0bW5AIaB45RrgU-mp9O-bCFWWa9NIsu8f-80FZEz-dUKIR6fZ9qeGBW83clfV3-L_zF/pubhtml?gid=0&single=true"

# Fazendo a requisição HTTP para obter o conteúdo da planilha
response = requests.get(sheet_url)
response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

# Parsing do conteúdo HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Vetores de dados que vão limitar a impressão dos editais
fatec_vetor = ['Sebrae','Itaquera','Atibaia','Itaquaquecetuba','Guarulhos','Ferraz de Vasconcelos','São Paulo','Osasco','Mauá','São Bernardo do Campo','São Caetano do Sul','Diadema','Tatuapé','Zona Leste'] # Exemplo: fatec_vetor = ["Tatuí", "Baixada Santista"]
curso_vetor = [] # Exemplo: curso_vetor = ["Gestão da Tecnologia da Informação", "Processos Gerenciais"]           
disciplina_vetor = [] # Exemplo: disciplina_vetor = ["PROJETOS DE TECNOLOGIA DA INFORMAÇÃO II", "Teoria das Organizações"]
area_disciplina_vetor = [] # Exemplo: area_disciplina_vetor = ["Ciência da computação", "Administração e negócios"]
determinado_vetor = [] # Exemplo: determinado_vetor = ["Determinado", "Indeterminado"]
periodo_aula_vetor = [] # Exemplo: periodo_aula_vetor = ["Noturno", "Vespertino"]

# obs: se o vetor estiver vazio, imprime todos os dados da coluna 

# Encontrando a tabela de editais
table = soup.find('table')

# Auxiliar para verificar se algum edital foi encontrado
flag_busca = 0

# Lista para armazenar os editais encontrados
editais_encontrados = []

if table:
    # Iterando sobre as linhas da tabela e extraindo as informações
    rows = table.find_all('tr')
    for row in rows[2:]:  # Pulando as duas primeiras linhas (labels e linha vazia)
        if 'height: 30px' in row.get('style', ''):  # Verificando se a linha contém dados
            cells = row.find_all(['td', 'th'])  # Incluindo 'th' para capturar todas as células
            if len(cells) >= 12:  # Verifica se há células suficientes na linha
                edital_no = cells[1].text.strip()
                fatec = cells[2].text.strip()
                curso = cells[3].text.strip()
                disciplina = cells[4].text.strip()
                area_disciplina = cells[5].text.strip()
                determinado = cells[6].text.strip()
                data_abertura = cells[7].text.strip()
                periodo_aula = cells[8].text.strip()
                data_limite = cells[9].text.strip()
                edital_link = cells[10].find('a')['href'] if cells[10].find('a') else 'N/A'
                ficha_link = cells[11].find('a')['href'] if cells[11].find('a') else 'N/A'
                tabela_pontuacao = cells[12].find('a')['href'] if cells[12].find('a') else 'N/A'

                # Verificando se o edital possui informações completas
                if edital_no and fatec and curso and disciplina and area_disciplina and determinado and data_abertura and periodo_aula and data_limite:
                    # Convertendo a data limite para um objeto datetime
                    data_limite_dt = datetime.strptime(data_limite, '%d/%m/%Y').date()
                    data_atual = datetime.now().date()
                    
                    # Verificando se a data atual é menor ou igual à data limite de inscrição
                    if data_atual <= data_limite_dt:
                        # Verificando se os dados estão presentes nos vetores
                        if (not fatec_vetor or fatec in fatec_vetor) and \
                           (not curso_vetor or curso in curso_vetor) and \
                           (not disciplina_vetor or disciplina in disciplina_vetor) and \
                           (not area_disciplina_vetor or area_disciplina in area_disciplina_vetor) and \
                           (not determinado_vetor or determinado in determinado_vetor) and \
                           (not periodo_aula_vetor or periodo_aula in periodo_aula_vetor):
                            flag_busca = 1
                            edital_info = {
                                "Edital No": edital_no,
                                "Fatec": fatec,
                                "Curso": curso,
                                "Disciplina": disciplina,
                                "Área(s) da disciplina": area_disciplina,
                                "Determinado ou indeterminado": determinado,
                                "Data de abertura para inscrição": data_abertura,
                                "Período da aula": periodo_aula,
                                "Data limite para inscrição": data_limite,
                                "Edital": edital_link,
                                "Ficha de Manifestação de Interesse": ficha_link,
                                "Tabela de Pontuação Docente": tabela_pontuacao
                            }
                            editais_encontrados.append(edital_info)

else:
    print("Tabela não encontrada na página.")
    exit(1)
    
if flag_busca == 1:
    print('Editais buscados com sucesso!')
else:
    print('Não possui editais com os indexadores indicados nos vetores!')
    exit(1)

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
y_inicio = pdf.get_y()
pdf.cell(0, 6, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)  # espaço inicial

# Cabeçalho do bloco
pdf.set_font("DejaVu", size=12)
pdf.cell(0, 8, text="https://cesu.cps.sp.gov.br/editaisabertos/",
         link='https://cesu.cps.sp.gov.br/editaisabertos/',
         new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
pdf.cell(0, 8, text="Tabelas de áreas, disciplinas e especificidades",
         link='https://cesu.cps.sp.gov.br/diretrizes-para-alteracao-de-carga-horaria-docente-concurso-publico-pss/',
         new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

# Resetando a cor do texto para preto
pdf.set_text_color(0, 0, 0)

# Formatando a data e hora no formato desejado
pdf.cell(0, 8, text=f"Data: {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
pdf.set_font("DejaVu", size=12)

for edital in editais_encontrados:
    # Estimar altura e quebrar página se necessário
    altura_bloco = 70  # ajuste conforme necessário
    if pdf.get_y() + altura_bloco > pdf.page_break_trigger:
        pdf.add_page()

    # Começo do "bloco"
    pdf.set_fill_color(240, 240, 240)  # cinza claro
    pdf.set_draw_color(200, 200, 200)
    y_inicio = pdf.get_y()
    pdf.cell(0, 6, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)  # espaço inicial

    # Cabeçalho do bloco
    pdf.set_font("DejaVu", size=12)
    pdf.cell(0, 8, text=f"Edital Nº {safe(edital['Edital No'])} - Fatec {safe(edital['Fatec'])}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
    pdf.set_font("DejaVu", size=12)

    # Linha 1 e 2
    pdf.cell(0, 6, text=f"Curso: {safe(edital['Curso'])}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, text=f"Disciplina: {safe(edital['Disciplina'])}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Linha 3
    pdf.cell(100, 6, text=f"Período: {safe(edital['Período da aula'])}", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(0, 6, text=f"Tipo: {safe(edital['Determinado ou indeterminado'])}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Linha 4
    pdf.cell(100, 6, text=f"Abertura: {safe(edital['Data de abertura para inscrição'])}", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(0, 6, text=f"Encerramento: {safe(edital['Data limite para inscrição'])}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Área e links
    pdf.multi_cell(0, 6, text=f"Área(s): {safe(edital['Área(s) da disciplina'])}")
    pdf.set_text_color(0, 0, 255)
    
    pdf.cell(0, 0, text="", new_x=XPos.LMARGIN, new_y=YPos.TOP)
    pdf.cell(0, 6, text="Link do Edital", link=safe(edital['Edital']), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, text="Ficha de Interesse", link=safe(edital['Ficha de Manifestação de Interesse']), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, text="Tabela de Pontuação", link=safe(edital['Tabela de Pontuação Docente']), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)

    # Espaço inferior
    pdf.cell(0, 4, text="", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

pdf.output("editais.pdf")
print("Arquivo editais.pdf gerado com sucesso com parâmetros atualizados!")
