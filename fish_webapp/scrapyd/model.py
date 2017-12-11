import json
from collections import namedtuple


def json2obj(data, class_name):
    return json.loads(data, object_hook=lambda d: namedtuple(class_name, d.keys())(*d.values()))


def obj2json(obj):
    return json.dumps(obj.__dict__)


class JobStatus():
    PENDING, RUNNING, FINISHED, CANCELED = range(4)


class JobPriority():
    LOW, NORMAL, HIGH, HIGHEST = range(4)


DEFAULT_TIME = '1970-01-01 00:00:00'


class BasicModel(object):
    def __str__(self):
        str = self.__class__.__name__ + ' object('
        for k, v in self.__dict__.items():
            str = str + '{}:{}, '.format(k, v)
        str = str[:len(str) - 2]
        str = str + ')'
        return str

    __repr__ = __str__

    def to_json(self):
        return obj2json(self)


class DaemonStatus(BasicModel):
    def __init__(self, status='error', running=0, pending=0, finished=0, node_name='error', json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.status = obj.status
            self.running = int(obj.running)
            self.pending = int(obj.pending)
            self.finished = int(obj.finished)
            self.node_name = obj.node_name
        else:
            self.status = status
            self.running = running
            self.pending = pending
            self.finished = finished
            self.node_name = node_name


class AddVersionResultSet(BasicModel):
    def __init__(self, status='error', spiders=0, json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.status = obj.status
            self.spiders = int(obj.spiders)
        else:
            self.status = status
            self.spiders = spiders


class ScheduleResultSet(BasicModel):
    def __init__(self, status='error', jobid='error', json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.status = obj.status
            self.jobid = obj.jobid
        else:
            self.status = status
            self.jobid = jobid


class CancelResultSet(BasicModel):
    def __init__(self, status='error', prevstate='error', json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.status = obj.status
            self.prevstate = obj.prevstate
        else:
            self.status = status
            self.prevstate = prevstate


class ProjectList(BasicModel):
    def __init__(self, status='error', projects=[], json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.status = obj.status
            self.projects = obj.projects
        else:
            self.status = status
            self.projects = projects


class VersionList(BasicModel):
    def __init__(self, status='error', versions=[], json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.status = obj.status
            self.versions = obj.versions
        else:
            self.status = status
            self.versions = versions


class SpiderList(BasicModel):
    def __init__(self, status='error', spiders=[], json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.status = obj.status
            self.spiders = obj.spiders
        else:
            self.status = status
            self.spiders = spiders


class JobList(BasicModel):
    def __init__(self, status='error',
                 pending=[],
                 running=[],
                 finished=[],
                 json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.status = obj.status
            self.pending = obj.pending
            self.running = obj.running
            self.finished = obj.finished
        else:
            self.status = status
            self.pending = pending
            self.running = running
            self.finished = finished


class DeleteProjectVersionResultSet(BasicModel):
    def __init__(self, status='error', json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.status = obj.status
        else:
            self.status = status


class DeleteProjectResultSet(BasicModel):
    def __init__(self, status='error', json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.status = obj.status
        else:
            self.status = status


class JobListDO(BasicModel):
    def __init__(self,
                 project_name='not found',
                 project_version='not found',
                 job_id='not found',
                 spider_name='not found',
                 args='empty',
                 logs_name=[],
                 logs_url=[],
                 creation_time=DEFAULT_TIME,
                 start_time=DEFAULT_TIME,
                 end_time=DEFAULT_TIME,
                 job_status=JobStatus.PENDING,
                 priority=JobPriority.LOW,
                 json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.project_name = obj.project_name
            self.project_version = obj.project_version
            self.job_id = obj.job_id
            self.spider_name = obj.spider_name
            self.args = obj.args
            self.logs_name = obj.logs_name
            self.logs_url = obj.logs_url
            self.creation_time = obj.creation_time
            self.start_time = obj.start_time
            self.end_time = obj.end_time
            self.job_status = obj.job_status
            self.priority = obj.priority
        else:
            self.project_name = project_name
            self.project_version = project_version
            self.job_id = job_id
            self.spider_name = spider_name
            self.args = args
            self.logs_name = logs_name
            self.logs_url = logs_url
            self.creation_time = creation_time
            self.start_time = start_time
            self.end_time = end_time
            self.job_status = job_status
            self.priority = priority


class ScrapydStatusVO(BasicModel):
    def __init__(self,
                 running=0,
                 pending=0,
                 finished=0,
                 project_amount=0,
                 spider_amount=0,
                 job_amount=0,
                 json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.running = obj.running
            self.pending = obj.pending
            self.finished = obj.finished
            self.project_amount = obj.project_amount
            self.spider_amount = obj.spider_amount
            self.job_amount = obj.job_amount
        else:
            self.running = running
            self.pending = pending
            self.finished = finished
            self.project_amount = project_amount
            self.spider_amount = spider_amount
            self.job_amount = job_amount


class ProjectListVO(BasicModel):
    def __init__(self,
                 project_name='not found',
                 project_versions='not found',
                 latest_project_version='not found',
                 spider_amount=0,
                 spider_names='not found',
                 pending_job_amount=0,
                 running_job_amount=0,
                 finished_job_amount=0,
                 json=None):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.project_name = obj.project_name
            self.project_versions = obj.versions
            self.latest_project_version = obj.latest_project_version
            self.spider_amount = obj.spider_amount
            self.spider_names = obj.spider_names
            self.pending_job_amount = obj.pending_job_amount
            self.running_job_amount = obj.running_job_amount
            self.finished_job_amount = obj.finished_job_amount
        else:
            self.project_name = project_name
            self.project_versions = project_versions
            self.latest_project_version = latest_project_version
            self.spider_amount = spider_amount
            self.spider_names = spider_names
            self.pending_job_amount = pending_job_amount
            self.running_job_amount = running_job_amount
            self.finished_job_amount = finished_job_amount


class SpiderListVO(BasicModel):
    def __init__(self,
                 spider_name='not found',
                 project_name='not found',
                 latest_project_version='not found',
                 logs_name=[],
                 logs_url=[],
                 pending_job_amount=0,
                 running_job_amount=0,
                 finished_job_amount=0,
                 json=None
                 ):
        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.spider_name = obj.spider_name
            self.project_name = obj.project_name
            self.latest_project_version = obj.latest_project_version
            self.logs_name = obj.logs_name
            self.logs_url = obj.logs_url
            self.pending_job_amount = obj.pending_job_amount
            self.running_job_amount = obj.running_job_amount
            self.finished_job_amount = obj.finished_job_amount
        else:
            self.spider_name = spider_name
            self.project_name = project_name
            self.latest_project_version = latest_project_version
            self.logs_name = logs_name
            self.logs_url = logs_url
            self.pending_job_amount = pending_job_amount
            self.running_job_amount = running_job_amount
            self.finished_job_amount = finished_job_amount
