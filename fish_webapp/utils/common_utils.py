def format_dict_to_str(dict, format):
    """
    Format a dictionary to the string, param format is a specified format rule
    such as dict = '{'name':'Sylvanas', 'gender':'Boy'}' format = '-'
    so result is 'name-Sylvanas, gender-Boy'.
    """
    result = ''
    for k, v in dict.items():
        result = result + str(k) + format + str(v) + ', '
    return result[:-2]

