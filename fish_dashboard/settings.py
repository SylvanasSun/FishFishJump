import os


class Config(object):
    DEBUG = False
    TESTING = False
    HOST = '0.0.0.0'
    PORT = '5000'
    SCRAPYD_URL = 'http://localhost:6800/'
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = '123456'
    CACHE_EXPIRE = 60  # second
    VERBOSE = False
    LOG_FILE_DIR = os.path.join(os.path.abspath('.'), 'log') + os.sep
    LOG_FILE_BASIS_NAME = 'fish_fish_jump_webapp.log'
    ELASTICSEARCH_HOSTS = 'localhost:9200'
    POLLING_INTERVAL_TIME = 3  # second
    FAILURE_SLEEP_TIME = 30  # second
    MAX_FAILURE_TIMES = 5
    MAX_FAILURE_MESSAGE_KEY = 'timeout_error'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
