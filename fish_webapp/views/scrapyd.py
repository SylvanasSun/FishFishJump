from flask import Blueprint, jsonify, current_app
from scrapyd.scrapyd_agent import ScrapydAgent
from scrapyd.scrapyd_service import get_scrapyd_status

scrapyd = Blueprint('scrapyd', __name__)

agent = None


def fetch_scrapyd_agent(scrapyd_url):
    global agent
    agent = ScrapydAgent(scrapyd_url)


@scrapyd.route('/status/chart', methods=['GET'])
def scrapyd_status():
    if current_app.config['ENABLE_CACHE']:
        result = current_app.config['GLOBAL_CACHE'].get('scrapyd_status')
        if result is None:
            result = get_scrapyd_status(agent)
            current_app.config['GLOBAL_CACHE'].set('scrapyd_status', result, timeout=current_app.config['CACHE_EXPIRE'])
            return jsonify(result.__dict__)
    else:
        return jsonify(get_scrapyd_status(agent).__dict__)
