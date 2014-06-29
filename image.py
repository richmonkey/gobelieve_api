from flask import request
from flask import Flask
import flask
import md5
from  thumbnail import *
from fs import FS
from flask import request, Blueprint
from util import make_response

app = Blueprint('image', __name__)

def image_ext(f):
    if f.content_type == "image/png":
        return ".png"
    elif f.content_type == "image/jpeg":
        return ".jpg"
    elif f.content_type:
        return ""
        
    if f.filename:
        _, ext = os.path.splitext(f.filename)
        return ext
    else:
        return ""



@app.route('/images', methods=['POST'])
def upload_image():
    f = request.files['file']
    ext = image_ext(f)
    if not ext:
        return make_response(400)

    data = f.read()
    name = md5.new(data).hexdigest()
    path = "/images/" + name + ext
    r = FS.upload(path, data)
    if not r:
        return flask.make_response("", 400)
    url = request.url_root + "images/" + name + ext
    src = "/images/" + name + ext
    obj = {"src":src, "src_url":url}
    return json.dumps(obj)

def download_thumbnail(path):
    tb_path = thumbnail_path(path)
    data = FS.download(tb_path)
    if not data:
        origin, params = parse_thumbnail_path(path)
        data = FS.download(origin)
        if not data:
            return ""
        data = create_thumbnail(data, params)
        r = FS.upload(tb_path, data)
        if not r:
            return ""
    return data
    
@app.route('/images/<image_path>', methods=['GET'])
def download_image(image_path):
    print image_path
    path = "/images/" + image_path
    if is_thumbnail(path):
        data = download_thumbnail(path)
    else:
        data = FS.download(path)

    if not data:
        return flask.make_response("", 400)
    else:
        return data
