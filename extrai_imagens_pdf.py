#  EXTRAI IMAGENS PDF
#  ESTE PROGRAMA LÊ UM ARQUIVO PDF E EXTRAI AS IMAGENS DO ARQUIVO EM UMA PASTA DESTINO.
#  DANIEL RODRIGUES DE SOUSA 09/06/2025

import fitz  # Importa a biblioteca PyMuPDF para manipulação de PDFs
import os    # Importa a biblioteca OS para lidar com diretórios e arquivos

def extrai_imagens_do_pdf(pdf_path, output_folder):
    try:
        # Tenta abrir o arquivo PDF
        pdf_document = fitz.open(pdf_path)
    except Exception as e:
        print(f"Erro ao abrir o arquivo PDF: {e}")
        return
    
    try:
        # Cria a pasta de saída, se ela ainda não existir
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    except Exception as e:
        print(f"Erro ao criar a pasta de saída: {e}")
        return
    
    try:
        # Itera por todas as páginas do PDF
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)  # Carrega a página atual
            image_list = page.get_images(full=True)  # Obtém todas as imagens da página
            
            # Itera por todas as imagens encontradas na página
            for img_index, img in enumerate(image_list):
                xref = img[0]  # Referência da imagem no PDF
                base_image = pdf_document.extract_image(xref)  # Extrai os dados da imagem
                image_bytes = base_image["image"]  # Conteúdo da imagem em bytes
                image_ext = base_image["ext"]      # Extensão do arquivo da imagem (ex: png, jpeg)
                
                # Define o nome do arquivo da imagem com base na página e índice
                image_filename = f"image_page{page_num + 1}_{img_index + 1}.{image_ext}"
                image_path = os.path.join(output_folder, image_filename)  # Caminho completo do arquivo
                
                try:
                    # Salva a imagem no disco
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                except Exception as e:
                    print(f"Erro ao salvar a imagem '{image_filename}': {e}")
                    return
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
        return
    
    # Mensagem de confirmação
    print(f"Imagens extraídas e salvas na pasta '{output_folder}'.")

# Exemplo de uso do programa
pdf_path = "seu_arquivo.pdf"  # Caminho do arquivo PDF (substitua pelo seu)
output_folder = "imagens_extraidas"  # Nome da pasta onde as imagens serão salvas
extrai_imagens_do_pdf(pdf_path, output_folder)