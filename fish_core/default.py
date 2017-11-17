MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = '%(spider)s'
MONGO_COLLECTION = '%(spider)s:items'

REDIS_START_URLS_KEY = "%(name)s:start_urls"
REDIS_START_URLS_AS_SET = False

SIMHASH_KEY = '%(spider)s:simhash_set'