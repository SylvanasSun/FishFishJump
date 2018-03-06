import os


class Config(object):
    DEBUG = False
    TESTING = False
    HOST = '0.0.0.0'
    PORT = '5009'
    VERBOSE = False
    LOG_FILE_DIR = os.path.join(os.path.abspath('.'), 'log') + os.sep
    LOG_FILE_BASIS_NAME = 'fish_fish_jump_searcher.log'
    ELASTICSEARCH_HOSTS = 'localhost:9200'
    ELASTICSEARCH_INDEX = ['pages']
    ELASTICSEARCH_DOC_TYPE = ['page_item']
    ENABLE_REDIS_FOR_CACHE = False
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
