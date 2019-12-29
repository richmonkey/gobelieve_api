# -*- coding: utf-8 -*-
from flask import request, Blueprint
from libs.util import make_response
from libs.fs import FS
import hashlib
import json
import subprocess
import os
import tempfile
from .authorization import require_auth

app = Blueprint('audio', __name__)

def NO_CONTENT():
    e = {"error":"上传内容为空"}
    return make_response(400, e)

def amr_to_mp3(data):
    f = tempfile.NamedTemporaryFile()
    f.write(data)
    f.flush()
    tmp = tempfile.mktemp()

    e = subprocess.call(["ffmpeg", "-i", f.name, "-f", "mp3", tmp])
    if e != 0:
        return None

    f.close()

    f = open(tmp, "rb")
    mp3_data = f.read()
    f.close()
    os.remove(tmp)
    return mp3_data



@app.route('/v2/audios', methods=['POST'])
@require_auth
def upload_form_file():
    if 'file' not in request.files:
        return NO_CONTENT()
    
    f = request.files['file']
    data = f.read()
    if not data:
        return NO_CONTENT()

    md5_value = hashlib.md5(data).hexdigest()
    path = "/audios/" + md5_value
    r = FS.upload(path, data)
    if not r:
        return make_response(400, {"error":"upload file fail"})
    
    
    obj = {}
    url = request.url_root + "audios/" + md5_value
    src = "/audio/" + md5_value
    obj["src"] = src
    obj["src_url"] = url
    return make_response(200, obj)
    


@app.route('/audios', methods=['POST'])
@require_auth
def upload_file():
    if not request.data:
        return NO_CONTENT()

    md5_value = hashlib.md5(request.data).hexdigest()
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
        return make_response(200, obj)


@app.route('/audios/<audio_path>.mp3')
def download_mp3(audio_path):
    path = "/audios/" + audio_path + ".mp3"
    data = FS.download(path)
    if not data:
        path = "/audios/" + audio_path
        amr_data = FS.download(path)
        if amr_data:
            data = amr_to_mp3(amr_data)
            path = "/audios/" + audio_path + ".mp3"
            FS.upload(path, data)
    
    if not data:
        return make_response(400)
    else:
        return data

@app.route('/audios/<audio_path>')
def download_file(audio_path):
    path = "/audios/" + audio_path
    data = FS.download(path)
    if not data:
        return make_response(400)
    else:
        return data
