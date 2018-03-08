#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time


def format_dict_to_str(dict, format):
    """
    Format a dictionary to the string, param format is a specified format rule
    such as dict = '{'name':'Sylvanas', 'gender':'Boy'}' format = '-'
    so result is 'name-Sylvanas, gender-Boy'.

    >>> dict = {'name': 'Sylvanas', 'gender': 'Boy'}
    >>> format_dict_to_str(dict, format='-')
    'name-Sylvanas, gender-Boy'
    """
    result = ''
    for k, v in dict.items():
        result = result + str(k) + format + str(v) + ', '
    return result[:-2]


def get_current_date(format='%Y-%m-%d %H:%M:%S'):
    return time.strftime(format, time.localtime())


def list_to_str(list, separator=','):
    """
    >>> list = [0, 0, 7]
    >>> list_to_str(list)
    '0,0,7'
    """
    list = [str(x) for x in list]
    return separator.join(list)


def str_to_list(str, separator):
    """
    >>> str = '0,0,7'
    >>> str_to_list(str, separator=',')
    ['0', '0', '7']
    """
    return str.split(separator)


def unite_dict(a, b):
    """
    >>> a = {'name': 'Sylvanas'}
    >>> b = {'gender': 'Man'}
    >>> unite_dict(a, b)
    {'name': 'Sylvanas', 'gender': 'Man'}
    """
    c = {}
    c.update(a)
    c.update(b)
    return c


def check_validity_for_dict(keys, dict):
    """
    >>> dict = {'a': 0, 'b': 1, 'c': 2}
    >>> keys = ['a', 'd', 'e']
    >>> check_validity_for_dict(keys, dict) == False
    True
    >>> keys = ['a', 'b', 'c']
    >>> check_validity_for_dict(keys, dict) == False
    False
    """
    for key in keys:
        if key not in dict or dict[key] is '' or dict[key] is None:
            return False
    return True
