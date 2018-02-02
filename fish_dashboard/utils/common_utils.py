import time


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


def get_current_date(format='%Y-%m-%d %H:%M:%S'):
    return time.strftime(format, time.localtime())


def list_to_str(list, separator=','):
    list = [str(x) for x in list]
    return separator.join(list)


def str_to_list(str, separator):
    return str.split(separator)

