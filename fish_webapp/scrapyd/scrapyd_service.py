from .model import ScrapydStatusVO


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
