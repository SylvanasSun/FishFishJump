.. image:: info/logo_904x487.png
    :target: https://github.com/SylvanasSun/FishFishJump

\

.. image:: https://img.shields.io/github/forks/SylvanasSun/FishFishJump.svg?style=social&label=Fork
    :target: https://github.com/SylvanasSun/FishFishJump
.. image:: https://img.shields.io/github/stars/SylvanasSun/FishFishJump.svg?style=social&label=Stars
    :target: https://github.com/SylvanasSun/FishFishJump
.. image:: https://img.shields.io/github/watchers/SylvanasSun/FishFishJump.svg?style=social&label=Watch
    :target: https://github.com/SylvanasSun/FishFishJump
.. image:: https://img.shields.io/github/followers/SylvanasSun.svg?style=social&label=Follow
    :target: https://github.com/SylvanasSun/FishFishJump

\


.. image:: https://img.shields.io/badge/Scrapy-1.4.0-blue.svg
    :target: https://github.com/scrapy/scrapy

.. image:: https://img.shields.io/badge/Flask-0.12.2-blue.svg
    :target: https://github.com/pallets/flask

.. image:: https://img.shields.io/badge/Redis-required-green.svg
    :target: https://redis.io/

.. image:: https://img.shields.io/badge/Elasticsearch-required-green.svg
    :target: https://www.elastic.co/

.. image:: https://img.shields.io/badge/MongoDB-required-green.svg
    :target: https://www.mongodb.com/

.. image:: https://img.shields.io/badge/docker-support-green.svg
    :target: https://www.docker.com/

\

.. image:: https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php
    :target: LICENSE

.. image:: https://travis-ci.org/SylvanasSun/FishFishJump.svg?branch=master
    :target: https://travis-ci.org/SylvanasSun/FishFishJump

.. image:: https://img.shields.io/pypi/pyversions/FishFishJump.svg
    :target: https://pypi.python.org/pypi/FishFishJump

.. image:: https://img.shields.io/pypi/v/FishFishJump.svg
    :target: https://pypi.python.org/pypi/FishFishJump

.. image:: https://img.shields.io/badge/version-0.2.3-brightgreen.svg
    :target: HISTORY.rst

.. image:: https://img.shields.io/github/release/SylvanasSun/FishFishJump.svg
    :target: https://github.com/SylvanasSun/FishFishJump

.. image:: https://img.shields.io/github/tag/SylvanasSun/FishFishJump.svg
    :target: https://github.com/SylvanasSun/FishFishJump

.. image:: https://img.shields.io/github/issues/SylvanasSun/FishFishJump.svg
    :target: https://github.com/SylvanasSun/FishFishJump

\

English_

.. _English: README.rst

FishFishJump是一个基于python的简单而基本的搜索引擎解决方案，该项目提供了多个可供参考且支持Docker自动化部署的Example，以帮助您实现定制化的搜索引擎网站。

.. image:: info/flow_chat.png

- **fish_core**: 包含一些其他模块所依赖的应用程序组件和工具。

- **fish_crawlers**: 基于scrapy-redis实现的分布式爬虫，它包含两个Scrapy项目：master_crawler将从http://dmoztools.net/抓取url并将其放入Redis队列，slave_crawler则从Redis队列拿到url，然后提取信息并存储到MongoDB中。

- **fish_dashboard**: 用于监控和管理Scrapy与Elasticsearch的web应用程序。

- **fish_searcher**: 支持搜索并返回查询结果的web应用程序，它依赖Elasticsearch与fish_crawler集群抓取到的数据。

Usage
---------

如果您想要独立部署这些Example，那么您只需要在项目的根目录下输入以下命令：

::

    docker-compose up -d --build

有关Docker和docker-compose的更多资料请参考: https://docs.docker.com/compose/

注意：对于fish_crawlers而言，您还需要进入到Docker容器之中并部署Scrapy项目，FishFishJump的部署方式使用Scrapyd，相关的配置文件位于scrapy.cfg中，例如：

::

    # Automatically created by: scrapy startproject
    #
    # For more information about the [deploy] section see:
    # https://scrapyd.readthedocs.org/en/latest/deploy.html

    [settings]
    default = master_crawler.settings

    [deploy:master_crawler01]
    url = http://127.0.0.1:6800/
    project = master_crawler

通过以下命令进行部署：

::

    # 进入Docker容器之中
    docker exec -it [container id] /bin/bash
    # 部署的命令为 'scrapyd-deploy [deploy name]', 关于deploy name参考文件scrapy.cfg
    cd master_crawler
    scrapyd-deploy master_crawler01
    cd ..
    cd slave_crawler
    scrapyd-deploy slave_crawler01
    # 启动爬虫, project与spider的名字同样参考scrapy.cfg
    # 爬虫dmoz_crawler需要在Redis中先存放一个key为dmoz_crawler:start_urls值为http://dmoztools.net/的数据以开始启动
    # Example: redis LPUSH dmoz_crawler:start_urls http://dmoztools.net/
    curl http://localhost:6800/schedule.json -d project=master_crawler -d spider=dmoz_crawler
    curl http://localhost:6800/schedule.json -d project=slave_crawler -d spider=simple_fish_crawler
    # 退出
    exit

更多资料请参考: https://github.com/scrapy/scrapyd-client

顺便说一下，fish_crawlers通过Docker自动在本地部署了Redis与MongoDB，如果您不想这样做，可以在docker-compose.yml文件中删除以下内容，然后在Scrapy项目下的setting.py配置文件中设置您的Redis与MongoDB的地址。

::

    redis:
        image: redis
        container_name: FishFishJump_Redis
        ports:
            - "6379:6379"

    mongo:
        image: mongo
        container_name: FishFishJump_Mongo
        ports:
            - "27017:27017"

      links:
        - redis
        - mongo


如果您不想使用Docker，也可以使用以下方式手动部署。

::

    # 需要先安装依赖
    pip install FishFishJump
    # 以下命令需要在Scrapy项目目录下执行
    scrapy crawl dmoz_crawler
    scrapy crawl simple_fish_crawler
    # 以下命令需要在fish_dashboard或者fish_searcher的根目录下执行
    python app.py

对于fish_crawlers，同样可以使用Scrapyd的部署方式进行部署（或者通过fish_dashboard远程管理）。


Dashboard
---------

fish_dashboard是用于监控Scrapy与Elasticsearch的健康状态和信息的监控平台，它提供了一些功能可以帮助您更好地管理Scrapy与Elasticsearch，例如：

- 通过ajax轮询实现实时显示数据，如果您不想使用这个功能，可以将配置POLLING_INTERVAL_TIME设置为0。

- 故障报警机制，当Scrapy或者Elasticsearch长时间没有响应时（根据配置属性MAX_FAILURE_TIMES），fish_dashboard将向您发送警报邮件。

- 传输数据机制，提供了两种方法将数据从MongoDB传输到Elasticsearch以生成索引库进行后续的搜索，第一种方法是手动全量传输，数据在离线状态下一次性传输到Elasticsearch，第二种方法是基于线程轮询实现的自动传输。

fish_dashboard基于Flask实现，其配置文件为fish_dashboard根目录下的settings.py，您也可以使用命令行接面，具体如下：

::

    Usage: fish_dashboard [options] args

    Command line param for FishFishJump webapp.

    Options:
    -h, --help            show this help message and exit
    --host=HOST           host address, default: 0.0.0.0
    --port=PORT           port, default: 5000
    --username=ADMIN_USERNAME
                            administrator username for login, default: admin
    --password=ADMIN_PASSWORD
                            administrator password for login, default: 123456
    -d, --debug           enable debug pattern of the flask, default: True
    -t, --test            enable test pattern of the flask, default: False
    --cached-expire=CACHE_EXPIRE
                            expire of the flask cache, default: 60
    --scrapyd-url=SCRAPYD_URL
                            url of the scrapyd for connect scrapyd service,
                            default: http://localhost:6800/
    -v, --verbose           verbose that log info, default: False
    --log-file-dir=LOG_FILE_DIR
                            the dir path of the where store log file, default:
                            E:\FishFishJump\log\
    --log-file-name=LOG_FILE_BASIS_NAME
                            the name of the what log file, default:
                            fish_fish_jump_webapp.log
    --elasticsearch-hosts=ELASTICSEARCH_HOSTS
                            the string represent a host address for Elasticsearch,
                            format: hostname:port and able to write multiple
                            address by comma separated default: localhost:9200
    --polling-interval=POLLING_INTERVAL_TIME
                            the time of the interval time for real-time dynamic
                            update, units second default: 3
    --failure-sleep-time=FAILURE_SLEEP_TIME
                            if connected fail will turn to this time window and
                            return backup data in this time window, units second
                            default: 30
    --max-failure-times=MAX_FAILURE_TIMES
                            the number of the max failure times if occurred fail
                            reaching the upper limit will sent message into the
                            front-end, default: 5
    --max-failure-message-key=MAX_FAILURE_MESSAGE_KEY
                            the string of the key for message sent after reaching
                            the upper limit, default: timeout_error


效果图：

.. image:: info/dashboard-01.png
.. image:: info/dashboard-02.png
.. image:: info/dashboard-03.gif
.. image:: info/dashboard-04.gif

Searcher
---------

fish_searcher是一个支持搜索和返回搜索结果的web应用程序，它基于Elasticsearch实现并提供了一些基本的搜索引擎所需要的功能。

.. image:: info/searching.gif

::

    Usage: fish_searcher [options] args

    Command line param for FishFishJump webapp.

    Options:
    -h, --help            show this help message and exit
    --host=HOST           host address, default: 0.0.0.0
    --port=PORT           port, default: 5009
    -d, --debug           enable debug pattern of the flask, default: True
    -t, --test            enable test pattern of the flask, default: False
    -v, --verbose         verbose that log info, default: False
    --log-file-dir=LOG_FILE_DIR
                            the dir path of the where store log file, default:
                            E:\FishFishJump\log\
    --log-file-name=LOG_FILE_BASIS_NAME
                            the name of the what log file, default:
                            fish_fish_jump_searcher.log
    --elasticsearch-hosts=ELASTICSEARCH_HOSTS
                            the string represent a host address for Elasticsearch,
                            format: hostname:port and able to write multiple
                            address by comma separated default: localhost:9200
    --elasticsearch-index=ELASTICSEARCH_INDEX
                            the string represents a list of the index for query
                            data from Elasticsearch, if you want to assign
                            multiple please separate with a comma, for example,
                            index_a,index_b, default: ['pages']
    --elasticsearch-doc-type=ELASTICSEARCH_DOC_TYPE
                            the string represents a list of the doc_type for query
                            data from Elasticsearch, if you want to assign
                            multiple please separate with a comma, for example,
                            doc_type_a, doc_type_b, default: ['page_item']
    --redis-cache           enable Redis for external cache, default: False
    --redis-host=REDIS_HOST
                            the string represents a host of the Redis and the
                            configuration invalid when not set config --redis-
                            cache, default: 127.0.0.1
    --redis-port=REDIS_PORT
                            the string represents a port of the Redis and the
                            configuration invalid when not set config --redis-
                            cache , default: 6379