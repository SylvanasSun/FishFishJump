from utils.common_utils import format_dict_to_str, get_current_date, list_to_str, str_to_list

from .model import ScrapydStatusVO, JobListDO, JobStatus, JobPriority, ProjectListVO, SpiderListVO
from .scrapyd_db import SqlLite3Agent


class ScrapydJobExtInfoSQLSet():
    TABLE_NAME = 'scrapyd_job_ext_info'
    DB_FILE_NAME = 'scrapyd.db'
    CREATE_TABLE = """CREATE TABLE %s (job_id VARCHAR(32) PRIMARY KEY, 
                    args VARCHAR(20), priority INT(1), 
                    creation_time DATE, logs_name VARCHAR(128), logs_url VARCHAR(255), 
                    project_name VARCHAR(32), project_version VARCHAR(20))""" % TABLE_NAME
    INSERT = 'INSERT INTO %s VALUES(?,?,?,?,?,?,?,?)' % TABLE_NAME
    SELECT_BY_ID = 'SELECT * FROM %s WHERE job_id = ?' % TABLE_NAME
    SELECT_ALL = 'SELECT * FROM %s' % TABLE_NAME
    DELETE_BY_ID = 'DELETE FROM %s WHERE job_id = ?' % TABLE_NAME
    DELETE_BY_PROJECT_NAME = 'DELETE FROM %s WHERE project_name = ?' % TABLE_NAME
    DELETE_BY_PROJECT_VERSION = 'DELETE FROM %s WHERE project_name = ? AND project_version = ?' % TABLE_NAME


def open_sqllite(sql_set):
    agent = SqlLite3Agent(sql_set.DB_FILE_NAME)
    agent.create_table(sql_set.CREATE_TABLE)
    return agent


sqllite_agent = open_sqllite(ScrapydJobExtInfoSQLSet)


def schedule_job(agent,
                 project_name,
                 spider_name,
                 priority=JobPriority.LOW,
                 setting=None,
                 job_id=None,
                 version=None,
                 args={}
                 ):
    jobid = agent.schedule(project_name, spider_name, priority, setting, job_id, version, args)['jobid']
    if version is None: version = agent.get_version_list(project_name)['versions'][-1:]
    # Save additional information that can't queried by scrapyd api into the database
    args_str = format_dict_to_str(args, '=')
    current_date = get_current_date()
    logs_name, logs_url = agent.get_logs(project_name, spider_name)
    sqllite_agent.execute(ScrapydJobExtInfoSQLSet.INSERT,
                          (jobid, args_str, priority, current_date, list_to_str(logs_name), list_to_str(logs_url),
                           project_name, version,))


def cancel_job(agent, project_name, job_id):
    """
    cancel a job.
    If the job is pending, it will be removed. If the job is running, it will be terminated.
    """
    prevstate = agent.cancel(project_name, job_id)['prevstate']
    if prevstate == 'pending':
        sqllite_agent.execute(ScrapydJobExtInfoSQLSet.DELETE_BY_ID, (job_id,))


def packing_job_ext_info(job_lsit_DO):
    """
    Packing additional information of the job into the job_list_DO(JobListDO)
    """
    ext_info = sqllite_agent.execute(ScrapydJobExtInfoSQLSet.SELECT_BY_ID, (job_lsit_DO.job_id,))
    if ext_info is None or len(ext_info) <= 0: return
    ext_info = ext_info[0]
    job_lsit_DO.args = ext_info[1]
    job_lsit_DO.priority = ext_info[2]
    job_lsit_DO.creation_time = ext_info[3]
    job_lsit_DO.logs_name = str_to_list(ext_info[4], ',')
    job_lsit_DO.logs_url = str_to_list(ext_info[5], ',')


def get_scrapyd_status(agent):
    # record the amount of the project and spider
    project_list = agent.get_project_list()['projects']
    spider_list = []
    for p in project_list:
        s = agent.get_spider_list(project_name=p)
        spider_list.extend(s['spiders'])
    # get load status of a scrapyd service
    load_status_dict = agent.get_load_status()
    running = load_status_dict['running']
    pending = load_status_dict['pending']
    finished = load_status_dict['finished']
    scrapydStatusVO = ScrapydStatusVO(running=running,
                                      pending=pending,
                                      finished=finished,
                                      project_amount=len(project_list),
                                      spider_amount=len(spider_list),
                                      job_amount=running + pending + finished
                                      )
    return scrapydStatusVO


def add_version(agent, project_name, version, egg):
    return agent.add_version(project_name, version, egg)['status']


def delete_project(agent, project_name):
    status = agent.delete_project(project_name)['status']
    if status == 'ok':
        sqllite_agent.execute(ScrapydJobExtInfoSQLSet.DELETE_BY_PROJECT_NAME, (project_name,))


def delete_project_version(agent, project_name, version):
    status = agent.delete_project_version(project_name, version)['status']
    if status == 'ok':
        sqllite_agent.execute(ScrapydJobExtInfoSQLSet.DELETE_BY_PROJECT_VERSION, (project_name, version,))


def get_all_job_list(agent):
    """
    Get all job list by each project name then
    return three job list on the base of different status(pending,running,finished).
    """
    project_list = agent.get_project_list()['projects']
    pending_job_list = []
    running_job_list = []
    finished_job_list = []
    for project_name in project_list:
        job_list = agent.get_job_list(project_name)
        # Extract latest version
        project_version = agent.get_version_list(project_name)['versions'][-1:]
        for pending_job in job_list['pending']:
            pending_job_list.append(JobListDO(project_name=project_name,
                                              project_version=project_version,
                                              job_id=pending_job['id'],
                                              spider_name=pending_job['spider'],
                                              job_status=JobStatus.PENDING
                                              ))
        for running_job in job_list['running']:
            running_job_list.append(JobListDO(project_name=project_name,
                                              project_version=project_version,
                                              job_id=running_job['id'],
                                              spider_name=running_job['spider'],
                                              start_time=running_job['start_time'],
                                              job_status=JobStatus.RUNNING
                                              ))
        for finished_job in job_list['finished']:
            finished_job_list.append(JobListDO(project_name=project_name,
                                               project_version=project_version,
                                               job_id=finished_job['id'],
                                               spider_name=finished_job['spider'],
                                               start_time=finished_job['start_time'],
                                               end_time=finished_job['end_time'],
                                               job_status=JobStatus.FINISHED
                                               ))

    return pending_job_list, running_job_list, finished_job_list


def get_all_project_list(agent):
    project_name_list = agent.get_project_list()['projects']
    project_list = []
    for project_name in project_name_list:
        version_list = agent.get_version_list(project_name)['versions']
        spider_list = agent.get_spider_list(project_name)['spiders']
        job_amounts = get_job_amounts(agent, project_name=project_name)
        project_list.append(ProjectListVO(project_name=project_name,
                                          project_versions=version_list,
                                          latest_project_version=version_list[-1:],
                                          spider_amount=len(spider_list),
                                          spider_names=spider_list,
                                          pending_job_amount=job_amounts['pending'],
                                          running_job_amount=job_amounts['running'],
                                          finished_job_amount=job_amounts['finished']
                                          ))
    return project_list


def get_all_spider_list(agent):
    project_name_list = agent.get_project_list()['projects']
    spider_list = []
    for project_name in project_name_list:
        spider_name_list = agent.get_spider_list(project_name)['spiders']
        latest_project_version = agent.get_version_list(project_name)['versions'][-1:]
        for spider_name in spider_name_list:
            logs_name, logs_url = agent.get_logs(project_name, spider_name)
            job_amounts = get_job_amounts(agent, project_name, spider_name)
            spider_list.append(SpiderListVO(spider_name=spider_name,
                                            project_name=project_name,
                                            latest_project_version=latest_project_version,
                                            logs_name=logs_name,
                                            logs_url=logs_url,
                                            pending_job_amount=job_amounts['pending'],
                                            running_job_amount=job_amounts['running'],
                                            finished_job_amount=job_amounts['finished']
                                            ))

    return spider_list


def get_job_amounts(agent, project_name, spider_name=None):
    """
    Get amounts that pending job amount, running job amount, finished job amount.
    """
    job_list = agent.get_job_list(project_name)
    pending_job_list = job_list['pending']
    running_job_list = job_list['running']
    finished_job_list = job_list['finished']
    job_amounts = {}
    if spider_name is None:
        job_amounts['pending'] = len(pending_job_list)
        job_amounts['running'] = len(running_job_list)
        job_amounts['finished'] = len(finished_job_list)
    else:
        job_amounts['pending'] = len([j for j in pending_job_list if j['spider'] == spider_name])
        job_amounts['running'] = len([j for j in running_job_list if j['spider'] == spider_name])
        job_amounts['finished'] = len([j for j in finished_job_list if j['spider'] == spider_name])

    return job_amounts


def get_logs_info(agent, project_name, spider_name):
    logs_name, logs_url = agent.get_logs(project_name, spider_name)
    return {'logs_name': logs_name, 'logs_url': logs_url}
