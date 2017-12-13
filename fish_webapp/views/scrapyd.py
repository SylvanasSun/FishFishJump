from flask import Blueprint, jsonify, current_app
from scrapyd.scrapyd_agent import ScrapydAgent
from scrapyd.scrapyd_service import get_scrapyd_status

scrapyd = Blueprint('scrapyd', __name__)

agent = None


class CacheKeys():
    SCRAPYD_STATUS_KEY = 'scrapyd_status'


def fetch_scrapyd_agent(scrapyd_url):
    global agent
    agent = ScrapydAgent(scrapyd_url)


@scrapyd.route('/status/chart', methods=['GET'])
def scrapyd_status():
    if current_app.config['ENABLE_CACHE']:
        result = current_app.config['GLOBAL_CACHE'].get(CacheKeys.SCRAPYD_STATUS_KEY)
        if result is None:
            result = get_scrapyd_status(agent)
            current_app.config['GLOBAL_CACHE'].set(CacheKeys.SCRAPYD_STATUS_KEY, result,
                                                   timeout=current_app.config['CACHE_EXPIRE'])
            return jsonify(result.__dict__)
    else:
        return jsonify(get_scrapyd_status(agent).__dict__)

