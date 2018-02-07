import datetime
import functools
import json
import logging
import os
import threading
import time

from bs4 import BeautifulSoup

from fish_core.utils.common_utils import unite_dict
from fish_core.utils.mail_utils import SmtpHelper, Attachment
from fish_dashboard.cache import set_cached, get_cached

lock = threading.Lock()

sleep_record = {}

fail_times = {}

backup = {}

logger = logging.getLogger(__name__)

ALARM_EMAIL_SENDER = 'FishFishJump'

MAX_FAILURE_TIMES = 'MAX_FAILURE_TIMES'

MAX_FAILURE_MESSAGE_KEY = 'MAX_FAILURE_MESSAGE_KEY'

MAX_FAILURE_MESSAGE = '<SERVER KEY %s> The number of the failure retry reach the upper limit'

FAILURE_SLEEP_TIME = 'FAILURE_SLEEP_TIME'

APP_BASIC_URL = None

alarm_email = None

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

EMAIL_ATTACHMENTS_PATH = os.path.join(ROOT_PATH, *['static', 'email_template'])

ALARM_EMAIL_ATTACHMENTS = [
    Attachment(path=os.path.join(EMAIL_ATTACHMENTS_PATH, 'logo.png'),
               filename='logo.png',
               maintype='image',
               subtype='png',
               id=0),
    Attachment(path=os.path.join(EMAIL_ATTACHMENTS_PATH, 'left.gif'),
               filename='left.gif',
               maintype='image',
               subtype='gif',
               id=1),
    Attachment(path=os.path.join(EMAIL_ATTACHMENTS_PATH, 'right.gif'),
               filename='right.gif',
               maintype='image',
               subtype='gif',
               id=2)
]


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
            if alarm_email is not None:
                _send_alarm_email('Happened fault!', MAX_FAILURE_MESSAGE % key)
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


def register_alarm_email(host, port, sender_addr, receiver,
                         receiver_addr, authorization_code, flask_app):
    global alarm_email
    alarm_email = AlarmEmail(sender=ALARM_EMAIL_SENDER,
                             sender_addr=sender_addr,
                             server_host=host,
                             server_port=port,
                             receiver=receiver,
                             receiver_addr=receiver_addr,
                             server_authorization=authorization_code)
    global APP_BASIC_URL
    APP_BASIC_URL = 'http://%s:%s' % (flask_app.config['HOST'], flask_app.config['PORT'])
    logger.info('Register alarm email (server %s:%s) is done' % (host, port))


def _send_alarm_email(subject, message):
    with open(os.path.join(EMAIL_ATTACHMENTS_PATH, 'fault_letter.html'), 'rb') as f:
        body = f.read()
    bs = BeautifulSoup(body, 'lxml')
    bs.find(id='message_body').string = message
    bs.find(id='app_url').href = APP_BASIC_URL
    alarm_email.add_attachments(ALARM_EMAIL_ATTACHMENTS)
    alarm_email.send_html(subject, bs.prettify())
    sender = '%s <%s>' % (alarm_email.sender, alarm_email.sender_addr)
    receiver = '%s <%s>' % (alarm_email.receiver, alarm_email.receiver_addr)
    logger.info('Send alarm email success (from %s into the %s)' % (sender, receiver))


class AlarmEmail(object):
    def __init__(self,
                 sender,
                 sender_addr,
                 receiver,
                 receiver_addr,
                 server_host,
                 server_port,
                 server_authorization):
        self.smtp_server = SmtpHelper()
        self.smtp_server.with_ssl() \
            .with_third_party_service() \
            .with_server(server_host, server_port) \
            .with_server_login(sender_addr, server_authorization) \
            .with_sender(sender, sender_addr) \
            .with_receiver(receiver, [receiver_addr])

    def send(self, subject, message):
        self.smtp_server.with_subject(subject).send(message)

    def send_html(self, subject, message):
        self.smtp_server.with_send_html().with_subject(subject).send(message)

    def add_attachments(self, attachments):
        self.smtp_server.with_attachment(attachments)
