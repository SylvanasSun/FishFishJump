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
    parser.add_option('--username',
                      help='administrator username for login, default: %s' % config.get('ADMIN_USERNAME'),
                      type='string',
                      dest='ADMIN_USERNAME',
                      default=config.get('ADMIN_USERNAME'))
    parser.add_option('--password',
                      help='administrator password for login, default: %s' % config.get('ADMIN_PASSWORD'),
                      dest='ADMIN_PASSWORD',
                      default=config.get('ADMIN_PASSWORD'))
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
    parser.add_option('--uncached',
                      help='disable cache of the flask, default: enable',
                      action='store_false',
                      dest='ENABLE_CACHE',
                      default=config.get('ENABLE_CACHE'))
    parser.add_option('--cached-expire',
                      help='expire of the flask cache, default: %s' % config.get('CACHE_EXPIRE'),
                      type='int',
                      dest='CACHE_EXPIRE',
                      default=config.get('CACHE_EXPIRE'))
    parser.add_option('--scrapyd-url',
                      help='url of the scrapyd for connect scrapyd service, default: %s' % config.get('SCRAPYD_URL'),
                      type='string',
                      dest='SCRAPYD_URL',
                      default=config.get('SCRAPYD_URL'))
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
    return parser.parse_args()


def enable_opts(config):
    opts, args = parse_opts(config)
    config.update(
        DEBUG=opts.DEBUG,
        TESTING=opts.TESTING,
        HOST=opts.HOST,
        PORT=opts.PORT,
        SCRAPYD_URL=opts.SCRAPYD_URL,
        ADMIN_USERNAME=opts.ADMIN_USERNAME,
        ADMIN_PASSWORD=opts.ADMIN_PASSWORD,
        ENABLE_CACHE=opts.ENABLE_CACHE,
        CACHE_EXPIRE=opts.CACHE_EXPIRE,
        VERBOSE=opts.VERBOSE,
        LOG_FILE_DIR=opts.LOG_FILE_DIR,
        LOG_FILE_BASIS_NAME=opts.LOG_FILE_BASIS_NAME,
        ELASTICSEARCH_HOSTS=opts.ELASTICSEARCH_HOSTS
    )
