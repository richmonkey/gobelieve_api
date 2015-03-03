from flask import request, Blueprint
from flask import redirect
import httpagentparser

app = Blueprint('download', __name__)

def platforms():
    r = request.environ
    user_agent = r.get('HTTP_USER_AGENT')
    if not user_agent:
        user_agent = request.headers.get('User-Agent')
    print user_agent
    agt_parsed = httpagentparser.detect(user_agent)
    str_platform = None

    if 'WOW64' in user_agent:
        str_platform = 'win32'
    elif 'Win64' in user_agent:
        str_platform = 'win64'
    else:
        if 'os' in agt_parsed:
            str_platform = agt_parsed['os']['name'].lower()
        if 'dist' in agt_parsed:
            str_platform = agt_parsed['dist']['name'].lower()

    return str_platform


@app.route("/download", methods=["GET"])
def download():
    platform = platforms()
    if platform == 'iphone' or platform == 'ipad' or platform == 'ios':
        package_url = "https://itunes.apple.com/us/app/yang-ti-jia/id923695740?mt=8"
    else:
        package_url = "http://gdown.baidu.com/data/wisegame/1e513446470ee74a/yangtijia_2.apk"

    return redirect(package_url)

