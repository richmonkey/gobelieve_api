from flask import request
from flask import Flask
import flask
import hashlib
import json
import os
from  libs.thumbnail import *
from libs.fs import FS
from flask import request, Blueprint
from werkzeug import secure_filename
from libs.util import make_response
from .authorization import require_auth
import logging

app = Blueprint('image', __name__)

def image_ext(content_type):
    if content_type == "image/png":
        return ".png"
    elif content_type == "image/jpeg":
        return ".jpg"
    else:
        return ""

@app.route("/v2/images", methods=['POST'])
@require_auth
def upload_form_image():
    if 'file' not in request.files:
        return make_response(400)
    
    f = request.files['file']
    content_type = f.headers.get("Content-Type", '')
    ext = image_ext(content_type)
    if not ext:
        return make_response(400, {"error":"can't get image extenstion"})

    data = f.read()
    if not data:
        return make_response(400, {"error":"data is null"})

    name = hashlib.md5(data).hexdigest()
    path = "/images/" + name + ext

    r = FS.upload(path, data)
    if not r:
        return make_response(400, {"error":"upload file fail"})
    
    url = request.url_root + "images/" + name + ext
    src = "/images/" + name + ext
    obj = {"src":src, "src_url":url}
    return make_response(200, data=obj)


@app.route('/images', methods=['POST'])
@require_auth
def upload_image():
    if not request.data:
        return make_response(400)

    content_type = request.headers.get("Content-Type", '')
    ext = image_ext(content_type)
    if not ext:
        return make_response(400)

    data = request.data
    name = hashlib.md5(data).hexdigest()
    path = "/images/" + name + ext
    r = FS.upload(path, data)
    if not r:
        return make_response(400)
    url = request.url_root + "images/" + name + ext
    src = "/images/" + name + ext
    obj = {"src":src, "src_url":url}
    return make_response(200, data=obj)

def download_thumbnail(path):
    tb_path = thumbnail_path(path)
    data = FS.download(tb_path)
    if not data:
        origin, params = parse_thumbnail_path(path)
        data = FS.download(origin)
        if not data:
            return ""
        print("data len:", len(data), type(data))
        data = create_thumbnail(data, params)
        r = FS.upload(tb_path, data)
        if not r:
            return ""
    return data
    
@app.route('/images/<image_path>', methods=['GET'])
def download_image(image_path):
    path = "/images/" + image_path
    if is_thumbnail(path):
        data = download_thumbnail(path)
    else:
        data = FS.download(path)

    if not data:
        return flask.make_response("", 400)
    else:
        res = flask.make_response(data, 200)
        if image_path.endswith(".jpg"):
            res.headers['Content-Type'] = "image/jpeg"
        elif image_path.endswith(".png"):
            res.headers['Content-Type'] = "image/png"
        else:
            logging.info("invalid image type")
        return res


