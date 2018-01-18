import os


class Config(object):
    DEBUG = False
    TESTING = False
    HOST = '0.0.0.0'
    PORT = '5000'
    SCRAPYD_URL = 'http://localhost:6800/'
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = '123456'
    ENABLE_CACHE = True
    CACHE_EXPIRE = 3 * 60  # second
    VERBOSE = False
    LOG_FILE_DIR = os.path.join(os.path.abspath('.'), 'log') + os.sep
    LOG_FILE_BASIS_NAME = 'fish_fish_jump_webapp.log'
    LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
