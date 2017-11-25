import logging

import requests

METHOD_GET = 'GET'
METHOD_POST = 'POST'

RETURN_TEXT = 'TEXT'
RETURN_BINARY = 'BINARY'
RETURN_JSON = 'JSON'
RETURN_RAW = 'RAW'


def before_logging(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        separator_idx = func_name.find('_')
        func_type = func_name[separator_idx + 1:]
        logging.debug('request[%s]: %s ....' % (func_type, args[0]))
        return func(*args, **kwargs)

    return wrapper


@before_logging
def request_get(url, data, retry_times=6):
    for i in range(retry_times):
        try:
            result = requests.get(url, params=data)
        except Exception as e:
            logging.warning('request[get]: %s - failure, retry times %s ' % (url, i + 1))
            continue
        return result


@before_logging
def request_post(url, data, retry_times=6):
    for i in range(retry_times):
        try:
            result = requests.post(url, data=data)
        except Exception as e:
            logging.warning('request[post]: %s - failure, retry times %s ' % (url, i + 1))
            continue
        return result


def request(url, data=None, method_type=METHOD_GET, retry_times=6, return_type=RETURN_TEXT):
    result = None
    if method_type == METHOD_GET:
        result = request_get(url, data, retry_times)
    if method_type == METHOD_POST:
        result = request_post(url, data, retry_times)

    if not result or result == None: return result
    if return_type == RETURN_TEXT:
        return result.text
    if return_type == RETURN_JSON:
        try:
            return result.json()
        except Exception as e:
            logging.warning('request[%s]: parse json failure %s ' % (method_type.lower(), str(e)))
    if return_type == RETURN_BINARY:
        return result.content
    if return_type == RETURN_RAW:
        return result.raw
