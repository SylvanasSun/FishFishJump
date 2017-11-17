# Created by SylvanasSun in 2017.10.26
# -*- coding: utf-8 -*-
import datetime

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.mail import MailSender


class SendEmailExtension(object):
    """
    Send email when scrapy start, close and error, configurate attribute of email at the settings.py.
    """

    def __init__(self, mailer, mail_to):
        self.mailer = mailer
        self.mail_to = mail_to
        self.processed_items_numbers = 0

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings['MAIL_TO']:
            raise NotConfigured('Not found configured MAIL_TO.')

        mailer = MailSender.from_settings(crawler.settings)
        ext = cls(mailer, crawler.settings['MAIL_TO'])

        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_errored, signal=signals.spider_error)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.item_record, signal=signals.item_passed)

        return ext

    def spider_opened(self, spider):
        subject = '%s began to crawl!' % spider.name
        body = """
               Hey guy, your crawler %s already crawling the data! ^_^
               date: %s
               """

        self.mailer.send(
            to=self.mail_to,
            subject=subject,
            body=body % (spider.name, self.get_current_date())
        )

    def spider_closed(self, spider):
        subject = '%s already over!' % spider.name
        body = """
               Hey guy, your crawler %s already done its work! ^_^
               processed items numbers: %s
               date: %s
               """

        self.mailer.send(
            to=self.mail_to,
            subject=subject,
            body=body % (spider.name, self.processed_items_numbers, self.get_current_date())
        )

    def spider_errored(self, failure, response, spider):
        subject = '%s come out error!' % spider.name
        body = """
               Hey guy, your crawler %s come out error when parse %s.
               error traceback: %s
               date: %s
               """
        body = body % (spider.name, response.url, failure.getTraceback(), self.get_current_date())

        self.mailer.send(
            to=self.mail_to,
            subject=subject,
            body=body
        )

    def item_record(self, item, spider):
        self.processed_items_numbers += 1

    def get_current_date(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
