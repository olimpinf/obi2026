Eu fiz esse formulário:https://docs.google.com/forms/d/e/1FAIpQLSdhS3FFIc2HTtyJZigwKyMMhMoWuYjUvwHL-G4VAI4JMY3FuA/viewform?usp=sharing

Aí você linka ele como o Google Sheets e adiciona as colunas:"Valor", "Valor por Extenso", "Local", "Data", "Justificativa 1", e "Justificativa 2".

O "Justifica 1" e "Justifica 2" são a primeira e a segunda linha da justificativa do recibo.

Meu Sheets ficou assim:https://docs.google.com/spreadsheets/d/1S8bM7MIv6805_GWAg-h8-hr8xWH1vTlNWBKYnWiUKlo/edit?usp=sharing

Aí precisa salvar a planilha do Sheets como csv e rodar o script preenche.py com esse arquivo na pasta. Ele vai gerar uma pasta xlsx com os arquivos do excel e uma pasta pdf com os recibos em pdf. E usará o primeiro e o último nome do aluno para montar o nome do arquivo.

Para gerar o PDF tem que ser no Mac e tem que ter o Excel instalado. Deve dar para mudar para OpenOffice mudando o Apple Script que tem lá dentro do .py. 

O arquivo atualizado.xlsx é uma versão minha do Anexo 7 da SBC. Eu tive que converter de xls para xlsx e tive que mudar o formato da imagem do logo para conseguir salvar. 