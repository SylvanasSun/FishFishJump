from flask import Blueprint, jsonify
from scrapyd.scrapyd_agent import ScrapydAgent
from scrapyd.scrapyd_service import get_scrapyd_status

scrapyd = Blueprint('scrapyd', __name__)

agent = None


def fetch_scrapyd_agent(scrapyd_url):
    global agent
    agent = ScrapydAgent(scrapyd_url)


@scrapyd.route('/status/chart', methods=['GET'])
def scrapyd_status():
    obj = get_scrapyd_status(agent)
    obj.run_amount = obj.running
    return jsonify(obj.__dict__)
