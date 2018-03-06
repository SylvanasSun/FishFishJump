from optparse import OptionParser


def parse_opts(config):
    parser = OptionParser(usage='usage: %prog [options] args',
                          description='Command line param for FishFishJump webapp.')
    parser.add_option('--host',
                      help='host address, default: %s' % config.get('HOST'),
                      dest='HOST',
                      type='string',
                      default=config.get('HOST'))
    parser.add_option('--port',
                      help='port, default: %s' % config.get('PORT'),
                      dest='PORT',
                      type='int',
                      default=config.get('PORT'))
    parser.add_option('-d',
                      '--debug',
                      help='enable debug pattern of the flask, default: %s' % config.get('DEBUG'),
                      action='store_true',
                      dest='DEBUG',
                      default=config.get('DEBUG'))
    parser.add_option('-t',
                      '--test',
                      help='enable test pattern of the flask, default: %s' % config.get('TESTING'),
                      action='store_true',
                      dest='TESTING',
                      default=config.get('TESTING'))
    parser.add_option('-v',
                      '--verbose',
                      help='verbose that log info, default: %s' % config.get('VERBOSE'),
                      action='store_true',
                      dest='VERBOSE',
                      default=config.get('VERBOSE'))
    parser.add_option('--log-file-dir',
                      help='the dir path of the where store log file, default: %s' % config.get('LOG_FILE_DIR'),
                      type='string',
                      dest='LOG_FILE_DIR',
                      default=config.get('LOG_FILE_DIR'))
    parser.add_option('--log-file-name',
                      help='the name of the what log file, default: %s ' % config.get('LOG_FILE_BASIS_NAME'),
                      type='string',
                      dest='LOG_FILE_BASIS_NAME',
                      default=config.get('LOG_FILE_BASIS_NAME'))
    parser.add_option('--elasticsearch-hosts',
                      help='the string represent a host address for Elasticsearch, format: hostname:port ' +
                           'and able to write multiple address by comma separated default: %s ' % config.get(
                               'ELASTICSEARCH_HOSTS'),
                      type='string',
                      dest='ELASTICSEARCH_HOSTS',
                      default=config.get('ELASTICSEARCH_HOSTS'))
    parser.add_option('--elasticsearch-index',
                      help='the string represents a list of the index for query data from Elasticsearch, if you want to assign multiple please separate with a comma, ' +
                           'for example, index_a,index_b, default: %s' % config.get('ELASTICSEARCH_INDEX'),
                      type='string',
                      dest='ELASTICSEARCH_INDEX',
                      default=config.get('ELASTICSEARCH_INDEX'))
    parser.add_option('--elasticsearch-doc-type',
                      help='the string represents a list of the doc_type for query data from Elasticsearch, if you want to assign multiple please separate with a comma, ' +
                           'for example, doc_type_a, doc_type_b, default: %s' % config.get('ELASTICSEARCH_DOC_TYPE'),
                      type='string',
                      dest='ELASTICSEARCH_DOC_TYPE',
                      default=config.get('ELASTICSEARCH_DOC_TYPE'))
    parser.add_option('--redis-cache',
                      help='enable Redis for external cache, default: %s' % config.get('ENABLE_REDIS_FOR_CACHE'),
                      action='store_true',
                      dest='ENABLE_REDIS_FOR_CACHE',
                      default=config.get('ENABLE_REDIS_FOR_CACHE'))
    parser.add_option('--redis-host',
                      help='the string represents a host of the Redis and the configuration invalid when not set config --redis-cache, default: %s'
                           % config.get('REDIS_HOST'),
                      type='string',
                      dest='REDIS_HOST',
                      default=config.get('REDIS_HOST'))
    parser.add_option('--redis-port',
                      help='the string represents a port of the Redis and the configuration invalid when not set config --redis-cache , default: %s'
                           % config.get('REDIS_PORT'),
                      type='int',
                      dest='REDIS_PORT',
                      default=config.get('REDIS_PORT'))

    return parser.parse_args()


def enable_opts(config):
    opts, args = parse_opts(config)
    config.update(
        DEBUG=opts.DEBUG,
        TESTING=opts.TESTING,
        HOST=opts.HOST,
        PORT=opts.PORT,
        VERBOSE=opts.VERBOSE,
        LOG_FILE_DIR=opts.LOG_FILE_DIR,
        LOG_FILE_BASIS_NAME=opts.LOG_FILE_BASIS_NAME,
        ELASTICSEARCH_HOSTS=opts.ELASTICSEARCH_HOSTS,
        ELASTICSEARCH_INDEX=opts.ELASTICSEARCH_INDEX,
        ELASTICSEARCH_DOC_TYPE=opts.ELASTICSEARCH_DOC_TYPE,
        ENABLE_REDIS_FOR_CACHE=opts.ENABLE_REDIS_FOR_CACHE,
        REDIS_HOST=opts.REDIS_HOST,
        REDIS_PORT=opts.REDIS_PORT
    )
