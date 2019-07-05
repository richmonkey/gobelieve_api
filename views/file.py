# -*- coding: utf-8 -*-
from flask import request, Blueprint
from libs.util import make_response
from libs.fs import FS
import hashlib
import json
import os
import logging
from .authorization import require_auth

app = Blueprint('file', __name__)

def NO_CONTENT():
    e = {"error":"上传内容为空"}
    return make_response(400, e)


@app.route('/files', methods=['POST'])
@require_auth
def upload_file():
    if 'file' not in request.files:
        return NO_CONTENT()

    #keep file extention
    f = request.files['file']
    _, ext = os.path.splitext(f.filename)
    data = f.read()
    if not data:
        return NO_CONTENT()
    
    md5_value = hashlib.md5(data).hexdigest()
    filename = md5_value + ext
    path = "/files/" + filename
    r = FS.upload(path, data)
    if not r:
        return make_response(400, {"error":"upload file fail"})
    
    obj = {}
    url = request.url_root + "files/" + filename
    src = "/files/" + filename
    obj["src"] = src
    obj["src_url"] = url
    return make_response(200, obj)

@app.route('/files/<file_path>')
def download_file(file_path):
    path = "/files/" + file_path
    data = FS.download(path)
    if not data:
        return make_response(400)
    else:
        return data

