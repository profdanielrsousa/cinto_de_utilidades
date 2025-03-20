#  QRCODE GENERATOR
#  ESTE PROGRAMA GERA UM QRCODE, PASSANDO UMA URL. SALVA NO ARQUIVO qrcode_personalizado.png
#  DANIEL RODRIGUES DE SOUSA 04/08/2024

import qrcode

# Insira o link
link = "https://encurtador.com.br/AgKPH"

# Crie o QRCode com opções de personalização
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=5,
    border=0)
qr.add_data(link)
qr.make(fit=True)
imagem = qr.make_image(fill_color="black", back_color="white")

# Salve a imagem personalizada
imagem.save("qrcode_personalizado.png")
