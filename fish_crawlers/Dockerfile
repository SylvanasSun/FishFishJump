FROM python:3.6-onbuild

ENV PATH /usr/local/bin:$PATH

MAINTAINER SylvanasSun sylvanas.sun@gmail.com

# scrapyd or scrapyd-client are not latest version when use pip intall
# so need manual installation.
RUN git clone https://github.com/scrapy/scrapyd.git
RUN git clone https://github.com/scrapy/scrapyd-client.git

RUN pip install -r requirements.txt

WORKDIR scrapyd
RUN python setup.py install
WORKDIR ..
WORKDIR scrapyd-client
RUN python setup.py install
WORKDIR ..

RUN mkdir /etc/scrapyd
RUN mkdir /etc/scrapyd/eggs
RUN mkdir /etc/scrapyd/logs
RUN mkdir /etc/scrapyd/items
RUN mkdir /etc/scrapyd/dbs
RUN \cp -rf scrapyd.conf /etc/scrapyd/scrapyd.conf

CMD ["scrapyd"]
