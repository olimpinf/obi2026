import re
import sys

DIVISOR = 11

CPF_WEIGHTS = ((10, 9, 8, 7, 6, 5, 4, 3, 2),
              (11, 10, 9, 8, 7, 6, 5, 4, 3, 2))
CNPJ_WEIGHTS = ((5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2),
               (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))


def clear_punctuation(document):
    """Remove from document all pontuation signals."""
    return re.sub(r'\D', '', str(document))

def calculate_first_digit(number):
    """ This function calculates the first check digit of a
        cpf or cnpj.
        :param number: cpf (length 9) or cnpf (length 12) 
            string to check the first digit. String with digits only.
        :returns: string -- the first digit
    """

    sum = 0
    if len(number) == 9:
        weights = CPF_WEIGHTS[0]
    else:
        weights = CNPJ_WEIGHTS[0]

    for i in range(len(number)):
        sum = sum + int(number[i]) * weights[i]
    rest_division = sum % DIVISOR
    if rest_division < 2:
        return '0'
    return str(11 - rest_division)


def calculate_second_digit(number):
    """ This function calculates the second check digit of
        a cpf or cnpj.
        **This function must be called after the above.**
        :param number: cpf (length 10) or cnpj 
            (length 13) number with the first digit. String with digits only.
        :returns: string -- the second digit
    """

    sum = 0
    if len(number) == 10:
        weights = CPF_WEIGHTS[1]
    else:
        weights = CNPJ_WEIGHTS[1]

    for i in range(len(number)):
        sum = sum + int(number[i]) * weights[i]
    rest_division = sum % DIVISOR
    if rest_division < 2:
        return '0'
    return str(11 - rest_division)

def validate_cnpj(number):
    """This function validates a CNPJ number.
    This function uses calculation package to calculate both digits
    and then validates the number.
    :param number: a CNPJ number to be validated, string with only digits
    :return: Bool -- True for a valid number, False otherwise.
    """

    _cnpj = clear_punctuation(number)

    if (len(_cnpj) != 14 or
       len(set(_cnpj)) == 1):
        return False

    first_part = _cnpj[:12]
    second_part = _cnpj[:13]
    first_digit = _cnpj[12]
    second_digit = _cnpj[13]

    if (first_digit == calculate_first_digit(first_part) and
       second_digit == calculate_second_digit(second_part)):
        return True

    return False

def validate_cpf(number):
    """This function validates a CPF number.
    :param number: a CPF number to be validated.  String with digits only
    :return: Bool -- True for a valid number, False otherwise.
    """

    _cpf = clear_punctuation(number)

    if (len(_cpf) != 11 or
       len(set(_cpf)) == 1):
        return False

    first_part = _cpf[:9]
    second_part = _cpf[:10]
    first_digit = _cpf[9]
    second_digit = _cpf[10]

    if (first_digit == calculate_first_digit(first_part) and
       second_digit == calculate_second_digit(second_part)):
        return True

    return False

def validate_cpf_cnpj(number):
    """This functions acts like a Facade to the other modules cpf and cnpj
       and validates either CPF and CNPJ numbers.
       :param number: a CPF or CNPJ number. Clear number to have only numbers.
       :type number: string
       :return: Formatted number is a valid CPF or CNPJ number,
                '' if it is not
    """
    clean_number = clear_punctuation(number)

    if len(clean_number) == 11:
        if validate_cpf(clean_number):
            n = str(clean_number)
            return f'{n[:3]}.{n[3:6]}.{n[6:9]}-{n[9:11]}'
    elif len(clean_number) == 14:
        if validate_cnpj(clean_number):
            n = str(clean_number)
            return f'{n[:2]}.{n[2:5]}.{n[5:8]}/{n[8:12]}-{n[12:14]}'

    return ''

if __name__=='__main__':

    number = sys.argv[1]
    print(number)
    print(validate_cpf_cnpj(number))
