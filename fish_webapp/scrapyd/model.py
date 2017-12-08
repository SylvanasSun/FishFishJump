import json
from collections import namedtuple


def json2obj(data, class_name):
    return json.loads(data, object_hook=lambda d: namedtuple(class_name, d.keys())(*d.values()))


def obj2json(obj):
    return json.dumps(obj.__dict__)


class SpiderStatus():
    PENDING, RUNNING, FINISHED, CANCELED = range(4)


class JobRunType():
    ONETIME = 'onetime'
    PERIODIC = 'periodic'


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


class JobVO(BasicModel):
    def __init__(self,
                 project_id=-1,
                 spider_name='error',
                 spider_status=SpiderStatus.PENDING,
                 creation_time=DEFAULT_TIME,
                 start_time=DEFAULT_TIME,
                 end_time=DEFAULT_TIME,
                 job_run_type=JobRunType.ONETIME,
                 job_priority=JobPriority.NORMAL,
                 json=None):

        if json is not None:
            obj = json2obj(json, self.__class__.__name__)
            self.project_id = int(obj.project_id)
            self.spider_name = obj.spider_name
            self.spider_status = int(obj.spider_status)
            self.creation_time = obj.creation_time
            self.start_time = obj.start_time
            self.end_time = obj.end_time
            self.job_run_type = obj.job_run_type
            self.job_priority = int(obj.job_priority)
        else:
            self.project_id = project_id
            self.spider_name = spider_name
            self.spider_status = spider_status
            self.creation_time = creation_time
            self.start_time = start_time
            self.end_time = end_time
            self.job_run_type = job_run_type
            self.job_priority = job_priority


class ScrapydStatusVO(BasicModel):
    def __init__(self,
                 running=0,
                 pending=0,
                 finished=0,
                 project_amount=0,
                 spider_amount=0,
                 job_amount=0):
        self.running = running
        self.pending = pending
        self.finished = finished
        self.project_amount = project_amount
        self.spider_amount = spider_amount
        self.job_amount = job_amount
