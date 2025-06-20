#  BUSCA DEMANDA VESTIBULAR FATEC
#  ESTE PROGRAMA LÊ OS DADOS DO SITE DA CESU (https://vestibular.fatec.sp.gov.br/demanda/), E FAZ UMA BUSCA DAS DEMANDAS, TODOS OS ANOS E TODAS AS UNIDADES.
#  NO FINAL, ELE GERA UM ARQUIVO CSV COM OS DADOS (todas_fatecs_demanda.csv).
#  DANIEL RODRIGUES DE SOUSA 19/06/2025

import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://vestibular.fatec.sp.gov.br/demanda/"

# Inicializa navegador para pegar anos disponíveis

# Abre navegador apenas para obter os anos
try:
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    driver.get(url)

    select_ano_elem = wait.until(EC.presence_of_element_located((By.NAME, "ano-sem")))
    select_ano = Select(select_ano_elem)
    anos_semestral = [opt.get_attribute("value") for opt in select_ano.options if opt.get_attribute("value")]
    del anos_semestral[0]  # Remove "Selecione..."
    driver.quit()
except Exception as e:
    print(f"[ERRO] ao busca o ano_sem para: {e}")

#teste
#anos_semestral = ["20231", "20251"]


with open("todas_fatecs_demanda.csv", mode="w", newline="", encoding="utf-8") as arquivo:
    escritor = csv.writer(arquivo)
    escritor.writerow(["Ano", "Semestre", "Unidade", "Curso", "Período", "Inscritos", "Vagas", "Demanda"])

    for ano_sem in anos_semestral:
        ano = ano_sem[:4]
        semestre = ano_sem[4]

        # Abre navegador apenas para obter as unidades válidas
        try:
            driver = webdriver.Chrome()
            wait = WebDriverWait(driver, 10)
            driver.get(url)

            select_ano = Select(wait.until(EC.presence_of_element_located((By.NAME, "ano-sem"))))
            select_ano.select_by_value(ano_sem)

            btn_exibir = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary[type='send']")))
            driver.execute_script("arguments[0].click();", btn_exibir)

            select_fatec = Select(wait.until(EC.presence_of_element_located((By.ID, "FATEC"))))
            lista_unidades = [o.get_attribute("value") for o in select_fatec.options if o.get_attribute("value")]

            driver.quit()
        except Exception as e:
            print(f"[ERRO] ao buscar unidades para {ano_sem}: {e}")
            continue

        # Itera sobre cada unidade para o ano atual
        for unidade in lista_unidades:
            try:
                driver = webdriver.Chrome()
                wait = WebDriverWait(driver, 10)
                driver.get(url)

                select_ano = Select(wait.until(EC.presence_of_element_located((By.NAME, "ano-sem"))))
                select_ano.select_by_value(ano_sem)

                btn_exibir = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary[type='send']")))
                driver.execute_script("arguments[0].click();", btn_exibir)

                select_fatec = Select(wait.until(EC.presence_of_element_located((By.ID, "FATEC"))))
                select_fatec.select_by_value(unidade)

                btn_exibir = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary[type='send']")))
                driver.execute_script("arguments[0].click();", btn_exibir)
                time.sleep(2)

                tabela = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-striped")))
                linhas = tabela.find_elements(By.TAG_NAME, "tr")[1:]

                for linha in linhas:
                    colunas = linha.find_elements(By.TAG_NAME, "td")
                    if len(colunas) == 5:
                        curso = colunas[0].text.strip().upper()
                        periodo = colunas[1].text.strip().upper()
                        inscritos = colunas[2].text.strip().upper()
                        vagas = colunas[3].text.strip().upper()
                        demanda = colunas[4].text.strip().upper()
                        unidade_upper = unidade.upper()
                        escritor.writerow([ano, semestre, unidade_upper, curso, periodo, inscritos, vagas, demanda])
                print(f"[OK] {ano_sem} - {unidade_upper}")
            except Exception as e:
                print(f"[ERRO] {ano_sem} - {unidade_upper}: {e}")
            finally:
                driver.quit()

print("Extração completa. Dados salvos em 'todas_fatecs_demanda.csv'.")
