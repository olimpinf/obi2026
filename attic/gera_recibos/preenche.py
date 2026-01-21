# pip install Pillow (apesar de não ter o import, mas o openpyxl precisa)
import os
from unidecode import unidecode
import pandas as pd
from openpyxl import load_workbook
import subprocess


posicoes = {
    # I4 - valor numérico do recibo - Ok
    "I4": "Valor",
    # B10 - valor por extenso do recibo - Ok
    "B10": "Valor por Extenso",
    # D11 - justificativa linha 1 - Ok
    "D11": "Justificativa 1",
    # B12 - justificativa linha 2 - Ok
    "B12": "Justificativa 2",
    # C17 - Nome
    "C17": "Nome Completo",
    # C18 - Endereço
    "C18": "Endereço",
    # C19 - Cidade
    "C19": "Cidade/Estado",
    # F19 - CEP
    "F19": "CEP",
    # C20 - CPF
    "C20": "CPF",
    # C21 - RG
    "C21": "RG/Emissor",
    # G20 - Local e Data
    "G20": "Local/Data",
    # C27 - Nome do Banco
    "C27": "Nome do Banco",
    # H27 - Número do Banco
    "H27": "Número do Banco",
    # C28 - Nome da Agência
    "C28": "Nome da Agência",
    # H28 - Número da Conta Corrente
    "H28": "Número da Conta Corrente",
    # C29 - Número da Agência
    "C29": "Número da Agência",
    # F30 - Nome do titular
    "F30": "Nome do Titular",
    # G31 - CPF do titular
    "G31": "CPF do Titular"
}

def read_data():
    # Define the file path or name
    file_name = "Dados para Ajuda de Custo (Responses) - Form Responses 1.csv"

    # Use pandas to read the CSV file
    df = pd.read_csv(file_name, dtype=str)

    # Convert the DataFrame to a list of dictionaries
    list_of_dicts = df.to_dict('records')
    
    return list_of_dicts


def sanitize_name(full_name):
    # Split the name into parts
    name_parts = full_name.split()

    # Get the first and last parts
    first_name = name_parts[0]
    last_name = name_parts[-1]

    # Return the sanitized name
    return unidecode(first_name.lower() + '_' + last_name.lower())


def save_as_pdf(excel_file, pdf_file):
    excel_file = os.getcwd() + "/" + excel_file
    pdf_file = os.getcwd() + "/" + pdf_file

    script = f'''
    tell application "Microsoft Excel"
        open "{excel_file}"
        save as active sheet filename "{pdf_file}" file format PDF file format --  as pdfs
    end tell
    '''
    osa_command = ['osascript', '-e', script]
    subprocess.run(osa_command)


def process(student):
    workbook = load_workbook(filename="atualizado.xlsx")
    sheet = workbook.active
    for k, v in posicoes.items():
        sheet[k] = student[v]

    safe = sanitize_name(student["Nome Completo"])
    workbook.save(filename=f"xlsx/{safe}.xlsx")
    save_as_pdf(f"xlsx/{safe}.xlsx", f"pdf/{safe}.pdf")

def fix_fields(student):
    for k, v in student.items():
        student[k] = str(v).strip()
    # Local,Data -> Local/Data
    student["Local/Data"] = student["Local"] + ", " + student["Data"]
    # RG,Emissor do RG -> RG/Emissor
    student["RG/Emissor"] = student["RG"] + " " + student["Emissor do RG"]
    # Rua/Avenida,Número,Complemento -> Endereço
    student["Endereço"] = student["Rua/Avenida"] + ", " + student["Número"] + " " + student["Complemento"]
    # Cidade, Estado -> Cidade/Estado
    student["Cidade/Estado"] = student["Cidade"] + ", " + student["Estado"]

def main():
    os.makedirs("xlsx", exist_ok=True)
    os.makedirs("pdf", exist_ok=True)
    data = read_data()
    for student in data:
        fix_fields(student)
        process(student)

if __name__ == '__main__':
    main()