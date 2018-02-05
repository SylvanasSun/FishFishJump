import datetime
import functools
import json
import logging
import threading
import time

from fish_core.utils.common_utils import unite_dict
from fish_dashboard.cache import set_cached, get_cached

lock = threading.Lock()

sleep_record = {}

fail_times = {}

backup = {}

logger = logging.getLogger(__name__)

MAX_FAILURE_TIMES = 'MAX_FAILURE_TIMES'

MAX_FAILURE_MESSAGE_KEY = 'MAX_FAILURE_MESSAGE_KEY'

MAX_FAILURE_MESSAGE = '<SERVER KEY %s> The number of the failure retry reach the upper limit'

FAILURE_SLEEP_TIME = 'FAILURE_SLEEP_TIME'


def use_backup_if_fail(app, key):
    """
    Return a error flag for prompt message in front-end  if failure times (unceasing fail)
    greater than max failure times else return backup data (latest data in the cache)
    """
    lock.acquire()
    try:
        if key not in backup:
            backup[key] = {}
        if key in fail_times and fail_times[key] % app.config[MAX_FAILURE_TIMES] == 0:
            logger.error(
                '<SERVER KEY %s> At present already reaching the upper limit of the max failure times, failure times: %s' % (
                    key, fail_times[key]))
            message = {app.config[MAX_FAILURE_MESSAGE_KEY]: MAX_FAILURE_MESSAGE % key}
            return unite_dict(backup[key], message)
        else:
            logger.info('<SERVER KEY %s> Request fail or in a status of sleep time window and return backup data %s' % (
                key, backup[key]))
            return backup[key]
    finally:
        lock.release()


def update_backup(app, key, data):
    lock.acquire()
    try:
        if get_cached(app, key) is None:
            set_cached(app, key, data)
            backup[key] = data
        else:
            backup[key] = get_cached(app, key)
    finally:
        lock.release()


def is_sleep(key):
    """
    Determine return data by use cache if this key is in the sleep time window(happened error)
    """
    lock.acquire()
    try:
        if key not in sleep_record:
            return False
        return time.time() < sleep_record[key]
    finally:
        lock.release()


def clean_sleep_record(key):
    lock.acquire()
    try:
        if key in sleep_record:
            del sleep_record[key]
        if key in fail_times:
            del fail_times[key]
        logger.info('<SERVER KEY %s> Request success and will clean sleep record and fail times' % key)
    finally:
        lock.release()


def generate_sleep_time_window(app, key):
    lock.acquire()
    try:
        sleep_record[key] = time.time() + app.config[FAILURE_SLEEP_TIME]
        if key not in fail_times:
            fail_times[key] = 1
        else:
            fail_times[key] = fail_times[key] + 1
        logger.info('<SERVER KEY %s> Request fail and will generate sleep record(%s) and fail times(%s)' % (
            key, datetime.datetime.fromtimestamp(sleep_record[key]), fail_times[key]))
    finally:
        lock.release()
    return fail_times[key]


def fault_tolerant_by_backup(flask_app, key, serializable_func=json.dumps):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            if is_sleep(key):
                return serializable_func(use_backup_if_fail(flask_app, key))
            try:
                result = func(*args, **kw)
                update_backup(flask_app, key, result)
                clean_sleep_record(key)
            except Exception:
                times = generate_sleep_time_window(flask_app, key)
                logger.warning('Server %s failure so now return backup data (failure times: %s)' % (key, times))
                return serializable_func(use_backup_if_fail(flask_app, key))
            return serializable_func(result)

        return wrapper

    return decorator
