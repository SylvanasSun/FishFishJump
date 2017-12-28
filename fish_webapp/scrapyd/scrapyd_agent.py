import sys
from html.parser import HTMLParser
import logging
from utils import http_utils

from .model import DaemonStatus, AddVersionResultSet, ScheduleResultSet, CancelResultSet, ProjectList, \
    VersionList, SpiderList, JobList, DeleteProjectVersionResultSet, DeleteProjectResultSet

logging = logging.getLogger(__name__)


class ScrapydLogsPageHTMLParser(HTMLParser):
    result = []

    def handle_data(self, data):
        # Extract text of the tag a for get log file name
        if self.lasttag == 'a':
            self.result.append(data)

    def clean_enter_sign(self):
        for x in self.result:
            if x.startswith('\n'):
                self.result.remove(x)


class ScrapydCommandSet(dict):
    def __init__(self, *args, **kw):
        super(ScrapydCommandSet, self).__init__(*args, **kw)
        self.itemlist = list(super(ScrapydCommandSet, self).keys())

    def __setitem__(self, key, value):
        self.itemlist.append(key)
        super(ScrapydCommandSet, self).__setitem__(key, value)

    def __iter__(self):
        return iter(self.itemlist)

    def keys(self):
        return self.itemlist

    def values(self):
        return [self[key] for key in self]

    def itervalues(self):
        return (self[key] for key in self)

    def init_command_set(self, scrapyd_url):
        """
         Initialize command set by scrapyd_url,each element is a list such as ['command','supported http method type']
        """

        if scrapyd_url[-1:] != '/':
            scrapyd_url = scrapyd_url + '/'
        self['daemonstatus'] = [scrapyd_url + 'daemonstatus.json', http_utils.METHOD_GET]
        self['addversion'] = [scrapyd_url + 'addversion.json', http_utils.METHOD_POST]
        self['schedule'] = [scrapyd_url + 'schedule.json', http_utils.METHOD_POST]
        self['cancel'] = [scrapyd_url + 'cancel.json', http_utils.METHOD_POST]
        self['listprojects'] = [scrapyd_url + 'listprojects.json', http_utils.METHOD_GET]
        self['listversions'] = [scrapyd_url + 'listversions.json', http_utils.METHOD_GET]
        self['listspiders'] = [scrapyd_url + 'listspiders.json', http_utils.METHOD_GET]
        self['listjobs'] = [scrapyd_url + 'listjobs.json', http_utils.METHOD_GET]
        self['delversion'] = [scrapyd_url + 'delversion.json', http_utils.METHOD_POST]
        self['delproject'] = [scrapyd_url + 'delproject.json', http_utils.METHOD_POST]
        self['logs'] = [scrapyd_url + 'logs/', http_utils.METHOD_GET]


class ScrapydAgent(object):
    def __init__(self, scrapyd_url):
        command_set = ScrapydCommandSet()
        command_set.init_command_set(scrapyd_url)
        self.command_set = command_set

    def get_load_status(self):
        """
        To check the load status of a service.
        :return: a dictionary that include json data.
                 example: { "status": "ok", "running": "0", "pending": "0", "finished": "0", "node_name": "node-name" }
        """
        url, method = self.command_set['daemonstatus'][0], self.command_set['daemonstatus'][1]
        response = http_utils.request(url, method_type=method, return_type=http_utils.RETURN_JSON)
        if response is None:
            logging.warning('%s failure: not found or connection fail' % sys._getframe().f_code.co_name)
            response = DaemonStatus().__dict__
        return response

    def add_version(self, project_name, version, egg):
        """
        Add a version to a project, creating the project if it doesn’t exist.
        :param project_name: the project name
        :param version:  the project version
        :param egg:  a Python egg containing the project’s code
        :return: a dictionary that status message
                 example: {"status": "ok", "spiders": 3}
        """
        url, method = self.command_set['addversion'][0], self.command_set['addversion'][1]
        data = {}
        data['project'] = project_name
        data['version'] = version
        data['egg'] = egg
        response = http_utils.request(url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        if response is None:
            logging.warning('%s failure: not found or connection fail' % sys._getframe().f_code.co_name)
            response = AddVersionResultSet().__dict__
        return response

    def schedule(self,
                 project_name,
                 spider_name,
                 priority=0,
                 setting=None,
                 job_id=None,
                 version=None,
                 args={}):
        """
        Schedule a spider run (also known as a job), returning the job id.
        :param project_name: the project name
        :param spider_name: the spider name
        :param priority: the run priority
        :param setting: a Scrapy setting to use when running the spider
        :param job_id: a job id used to identify the job, overrides the default generated UUID
        :param version: the version of the project to use
        :param args: passed as spider argument
        :return: a dictionary that status message
                 example: {"status": "ok", "jobid": "6487ec79947edab326d6db28a2d86511e8247444"}
        """
        url, method = self.command_set['schedule'][0], self.command_set['schedule'][1]
        data = {}
        data['project'] = project_name
        data['spider'] = spider_name
        data['priority'] = priority
        if setting is not None:
            data['setting'] = setting
        if job_id is not None:
            data['jobid'] = job_id
        if version is not None:
            data['_version'] = version
        for k, v in args.items():
            data[k] = v
        response = http_utils.request(url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        if response is None:
            logging.warning('%s failure: not found or connection fail' % sys._getframe().f_code.co_name)
            response = ScheduleResultSet().__dict__
        return response

    def cancel(self, project_name, job_id):
        """
        Cancel a spider run (aka. job). If the job is pending, it will be removed. If the job is running, it will be terminated.
        :param project_name: the project name
        :param job_id: the job id
        :return: a dictionary that status message
                 example: {"status": "ok", "prevstate": "running"}
        """
        url, method = self.command_set['cancel'][0], self.command_set['cancel'][1]
        data = {}
        data['project'] = project_name
        data['job'] = job_id
        response = http_utils.request(url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        if response is None:
            logging.warning('%s failure: not found or connection fail' % sys._getframe().f_code.co_name)
            response = CancelResultSet().__dict__
        return response

    def get_project_list(self):
        """
        Get the list of projects uploaded to this Scrapy server.
        :return: a dictionary that project name list
                 example: {"status": "ok", "projects": ["myproject", "otherproject"]}
        """
        url, method = self.command_set['listprojects'][0], self.command_set['listprojects'][1]
        response = http_utils.request(url, method_type=method, return_type=http_utils.RETURN_JSON)
        if response is None:
            logging.warning('%s failure: not found or connection fail' % sys._getframe().f_code.co_name)
            response = ProjectList().__dict__
        return response

    def get_version_list(self, project_name):
        """
        Get the list of versions available for some project.
        The versions are returned in order, the last one is the currently used version.
        :param project_name: the project name
        :return: a dictionary that version name list
                 example: {"status": "ok", "versions": ["r99", "r156"]}
        """
        url, method = self.command_set['listversions'][0], self.command_set['listversions'][1]
        data = {'project': project_name}
        response = http_utils.request(url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        if response is None:
            logging.warning('%s failure: not found or connection fail' % sys._getframe().f_code.co_name)
            response = VersionList().__dict__
        return response

    def get_spider_list(self, project_name, version=None):
        """
        Get the list of spiders available in the last (unless overridden) version of some project.
        :param project_name: the project name
        :param version: the version of the project to examine
        :return: a dictionary that spider name list
                 example: {"status": "ok", "spiders": ["spider1", "spider2", "spider3"]}
        """
        url, method = self.command_set['listspiders'][0], self.command_set['listspiders'][1]
        data = {}
        data['project'] = project_name
        if version is not None:
            data['_version'] = version
        response = http_utils.request(url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        if response is None:
            logging.warning('%s failure: not found or connection fail' % sys._getframe().f_code.co_name)
            response = SpiderList().__dict__
        return response

    def get_job_list(self, project_name):
        """
        Get the list of pending, running and finished jobs of some project.
        :param project_name: the project name
        :return: a dictionary that list inculde job name and status
                 example:
                 {"status": "ok",
                    "pending": [{"id": "78391cc0fcaf11e1b0090800272a6d06", "spider": "spider1"}],
                    "running": [{"id": "422e608f9f28cef127b3d5ef93fe9399", "spider": "spider2",
                    "start_time": "2012-09-12 10:14:03.594664"}],
                    "finished": [{"id": "2f16646cfcaf11e1b0090800272a6d06", "spider": "spider3",
                    "start_time": "2012-09-12 10:14:03.594664", "end_time": "2012-09-12 10:24:03.594664"}]}
        """
        url, method = self.command_set['listjobs'][0], self.command_set['listjobs'][1]
        data = {'project': project_name}
        response = http_utils.request(url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        if response is None:
            logging.warning('%s failure: not found or connection fail' % sys._getframe().f_code.co_name)
            response = JobList().__dict__
        return response

    def delete_project_version(self, project_name, version):
        """
        Delete a project version.
        If there are no more versions available for a given project, that project will be deleted too.
        :param project_name: the project name
        :param version: the project version
        :return: a dictionary that status message
                 example: {"status": "ok"}
        """
        url, method = self.command_set['delversion'][0], self.command_set['delversion'][1]
        data = {'project': project_name, 'version': version}
        response = http_utils.request(url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        if response is None:
            logging.warning('%s failure: not found or connection fail' % sys._getframe().f_code.co_name)
            response = DeleteProjectVersionResultSet().__dict__
        return response

    def delete_project(self, project_name):
        """
        Delete a project and all its uploaded versions.
        :param project_name: the project name
        :return: a dictionary that status message
                 example: {"status": "ok"}
        """
        url, method = self.command_set['delproject'][0], self.command_set['delproject'][1]
        data = {'project': project_name}
        response = http_utils.request(url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        if response is None:
            logging.warning('%s failure: not found or connection fail' % sys._getframe().f_code.co_name)
            response = DeleteProjectResultSet().__dict__
        return response

    def get_logs(self, project_name, spider_name):
        """
        Get urls that scrapyd logs file by project name and spider name
        :param project_name: the project name
        :param spider_name: the spider name
        :return: two list of the logs file name and logs file url
        """
        url, method = self.command_set['logs'][0] + project_name + '/' + spider_name + '/', self.command_set['logs'][1]
        response = http_utils.request(url, method_type=method)
        html_parser = ScrapydLogsPageHTMLParser()
        html_parser.feed(response)
        html_parser.clean_enter_sign()
        return html_parser.result, [url + x for x in html_parser.result]
