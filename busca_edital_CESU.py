#  BUSCA EDITAL CESU
#  ESTE PROGRAMA LÊ OS DADOS DO SITE DA CESU (https://cesu.cps.sp.gov.br/editaisabertos/), POSSIBILITANDO A FILTRAGEM DOS DADOS.
#  NO FINAL, ELE GERA UM ARQUIVO EM PDF COM OS EDITAIS DE INTERESSE (editais.pdf).
#  DANIEL RODRIGUES DE SOUSA 19/03/2025

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF

# URL da planilha do Google Sheets
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSPxryxjiyOz0bW5AIaB45RrgU-mp9O-bCFWWa9NIsu8f-80FZEz-dUKIR6fZ9qeGBW83clfV3-L_zF/pubhtml?gid=0&single=true"

# Fazendo a requisição HTTP para obter o conteúdo da planilha
response = requests.get(sheet_url)
response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

# Parsing do conteúdo HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Vetores de dados que vão limitar a impressão dos editais
fatec_vetor = ['São Paulo','Guarulhos','Mauá','Itaquaquecetuba','Zona Leste','Ferraz de Vasconcelos','Tatuapé'] # Exemplo: fatec_vetor = ["Tatuí", "Baixada Santista"]
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
if editais_encontrados:
    pdf = FPDF(orientation='P')  # Mudando a orientação para retrato
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=12)  # Definindo o texto em negrito
   
    # Mudando a cor do texto para vermelho antes de adicionar o hiperlink
    pdf.set_text_color(255, 0, 0)
    
    pdf.cell(200, 6, txt="-" * 134, ln=True)
    pdf.cell(200, 6, txt="https://cesu.cps.sp.gov.br/editaisabertos/", link='https://cesu.cps.sp.gov.br/editaisabertos/', ln=True)
    
    # Formatando a data e hora no formato desejado
    data_formatada = data_atual.strftime('%d/%m/%Y, %H:%M:%S')

    pdf.cell(200, 6, txt=f"Data: {data_formatada}", ln=True)
    pdf.cell(200, 6, txt="-" * 134, ln=True)
    pdf.cell(200, 6, txt="" * 134, ln=True)
    
    # Resetando a cor do texto para preto
    pdf.set_text_color(0, 0, 0)

    pdf.set_font("Arial", size=12)

    for edital in editais_encontrados:
        pdf.cell(200, 6, txt=f"Edital No: {edital['Edital No']}", ln=True)
        pdf.cell(200, 6, txt=f"Fatec: {edital['Fatec']}", ln=True)
        pdf.cell(200, 6, txt=f"Curso: {edital['Curso']}", ln=True)
        pdf.cell(200, 6, txt=f"Disciplina: {edital['Disciplina']}", ln=True)
        pdf.multi_cell(200, 6, txt=f"Área(s) da disciplina: {edital['Área(s) da disciplina']}")
        pdf.cell(200, 6, txt=f"Determinado ou indeterminado: {edital['Determinado ou indeterminado']}", ln=True)
        pdf.cell(200, 6, txt=f"Data de abertura para inscrição: {edital['Data de abertura para inscrição']}", ln=True)
        pdf.cell(200, 6, txt=f"Período da aula: {edital['Período da aula']}", ln=True)
        pdf.cell(200, 6, txt=f"Data limite para inscrição: {edital['Data limite para inscrição']}", ln=True)
        
        # Mudando a cor do texto para vermelho antes de adicionar o hiperlink
        pdf.set_text_color(255, 0, 0)
        
        pdf.cell(200, 6, txt="Edital: link", link=edital['Edital'], ln=True)
        pdf.cell(200, 6, txt="Ficha de Manifestação de Interesse: link", link=edital['Ficha de Manifestação de Interesse'], ln=True)
        pdf.cell(200, 6, txt="Tabela de Pontuação Docente: link", link=edital['Tabela de Pontuação Docente'], ln=True)
        
        # Resetando a cor do texto para preto
        pdf.set_text_color(0, 0, 0)
        
        pdf.cell(200, 6, txt="-" * 134, ln=True)

    pdf.output("editais.pdf")
    print("Arquivo editais.pdf gerado com sucesso!")
else:
    print("Nenhum edital encontrado de acordo com os critérios. Arquivo PDF não gerado.")
    
exit(0)