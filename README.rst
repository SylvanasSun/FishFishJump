.. image:: info/logo_904x487.png
    :target: https://pypi.python.org/pypi/FishFishJump

.. image:: https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php
    :target: https://pypi.python.org/pypi/FishFishJump
.. image:: https://img.shields.io/pypi/pyversions/Django.svg
    :target: https://pypi.python.org/pypi/FishFishJump
.. image:: https://img.shields.io/badge/Scrapy-1.4.0-blue.svg
    :target: https://pypi.python.org/pypi/FishFishJump
.. image:: https://img.shields.io/badge/Flask-0.12.2-blue.svg
    :target: https://pypi.python.org/pypi/FishFishJump
.. image:: https://img.shields.io/badge/Redis-required-green.svg
    :target: https://pypi.python.org/pypi/FishFishJump
.. image:: https://img.shields.io/badge/Elasticsearch-required-green.svg
    :target: https://pypi.python.org/pypi/FishFishJump
.. image:: https://img.shields.io/badge/MongoDB-required-green.svg
    :target: https://pypi.python.org/pypi/FishFishJump
.. image:: https://img.shields.io/docker/automated/jrottenberg/ffmpeg.svg
    :target: https://pypi.python.org/pypi/FishFishJump

FishFishJump is a solution that simply and basic for search engines and provide multiple demos that independent deployment by used Docker.

- **fish_core**: Include some common utils or components and other modules depend on it.

- **fish_crawlers**: A demo of the distributed crawler that implements base on scrapy-redis, it contains two projects of scrapy, the master_crawler will crawl link from http://dmoztools.net/ and put it to the Redis queue, the slave_crawler will crawl the link from the Redis queue then extract info and store into the MongoDB.

- **fish_dashboard**: A web app for monitoring health status and info of  Scrapy and Elasticsearch base on Flask.

Usage
---------

If you want to independent deployments then you only need input following order in root directory of the fish_crawler or fish_dashboard:

::

    docker-compose up -d

More about docker and docker-compose please refer to: https://docs.docker.com/compose/

Notice: for fish_crawlers, you also need to access the Docker container and deploy scrapy, FishFishJump deployment way use Scrapyd, the related configuration file is in the scrapy.cfg such as:

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

Look at the following command to deployments:

::

    # enter in inside of the Docker container
    docker exec -it [container id] /bin/bash
    # register scrapy (need is in the root directory of the target scrapy project)
    scrapyd-deploy
    # start a crawler
    # project_name and spider_name refer to scrapy.cfg, the following examples are slave_crawler
    curl http://localhost:6800/schedule.json -d project=slave_crawler -d spider=simple_fish_crawler
    # exit from the Docker container
    exit

More about please refer to: https://github.com/scrapy/scrapyd-client

By the way, fish_crawlers use local Redis and MongoDB by Docker. if you don't want to then you can delete the following content in docker-compose.yml and config your Redis and MongoDB address in Scrapy project(settings.py).

::

    redis:
        image: redis
        container_name: FishFishJump_redis
        ports:
            - "6379:6379"

    mongo:
        image: mongo
        container_name: FishFishJump_mongo
        ports:
            - "27017:27017"

      links:
        - redis
        - mongo


if you want not use Docker then you need manual start fish_crawlers or fish_dashboard, please input following order:

::

    # the first need install dependency
    pip install FishFishJump
    # if on the root directory of the master_crawler
    scrapy crawl dmoz_crawler
    # if on the root directory of the slave_crawler
    scrapy crawl simple_fish_crawler
    # if on the root directory of the fish_dashboard
    python app.py

For fish_crawlers you can also use scrapyd for deployments.


Dashboard
---------

fish_dashboard is a monitoring platform that monitoring health status and information of the Scrapy and Elasticsearch and it has some feature help you better for manage Scrpay and Elasticsearch such as:

- real-time update data display by ajax polling if you don't want to use it you can set config POLLING_INTERVAL_TIME to 0 for cancel ajax polling.

- fault alarm mechanism, fish_dashboard will send an alarm email to you when your Scrapy or Elasticsearch there  was no response for a long time(reach maximum fault number of times, this param refer to MAX_FAILURE_TIMES in the settings.py).

- transfer data mechanism, you have two methods to transfer data from MongoDB into the Elasticsearch for generating index database for search, the first way is the manual transfer and data is transmitted at one time in the off-line state, the second way is the automatic transfer data based on a thread polling implementation and this thread will always transfer data from MongoDB into the Elasticsearch until you cancel it.

fish_dashboard is based on a Flask implementation and its config file is settings.py in the root directory of the fish_dashboard you can also use command line interface, the specific configuration is as following:

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


Here are some renderings:

.. image:: info/dashboard-01.png
.. image:: info/dashboard-02.png
.. image:: info/dashboard-03.gif
.. image:: info/dashboard-04.gif