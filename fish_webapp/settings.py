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


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
