# -*- coding: utf-8 -*-
from flask import request, Blueprint
from util import make_response
from fs import FS
import md5

app = Blueprint('audio', __name__)

def NO_CONTENT():
    e = {"error":"上传内容为空"}
    return make_response(400, e)

@app.route('/audios', methods=['POST'])
def upload_file():
    if not request.data:
        return NO_CONTENT()

    md5_value = md5.new(request.data).hexdigest()
    path = "/audios/" + md5_value
    r = FS.upload(path, request.data)
    if not r:
        return make_response(400)
    else:
        obj = {}
        url = request.url_root + "audios/" + md5_value
        src = "/audio/" + md5_value
        obj["src"] = src
        obj["src_url"] = url
        return make_response(200, json.dumps(obj))

@app.route('/audios/<audio_path>')
def download_file(audio_path):
    path = "/audios/" + audio_path
    data = FS.download(path)
    if not data:
        return make_response(400)
    else:
        return data
