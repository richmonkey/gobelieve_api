import os
from io import BytesIO
from PIL import Image

def parse_param(p):
    width = 0
    height = 0
    cut = 0
    n, e = os.path.splitext(p)
    params = n.split("_")
    for pa in params:
        if pa[-1] == 'w':
            width = int(pa[:-1])
        elif pa[-1] == 'h':
            height = int(pa[:-1])
        elif pa[-1] == 'c':
            cut = int(pa[:-1])
        else:
            logging.error("unknown image param")
    return width, height, cut

def validate_thumbnail_size(w, h):
    if w == 128 and h == 128:
        return True
    elif w == 256 and h == 256:
        return True
    else:
        return False

def parse_thumbnail_path(image_path):
    ps = image_path.split("@")
    if len(ps) == 1:
        return None, None

    origin, t = ps
    width, height, cut = parse_param(t)
    if not width or not height:
        return None, None
    if not validate_thumbnail_size(width, height):
        return None, None
        
    return origin, (width, height, cut)

def is_thumbnail(image_path):
    origin, _ = parse_thumbnail_path(image_path)
    return True if origin else False

def thumbnail_path(image_path):
    origin, params = parse_thumbnail_path(image_path)
    if not origin:
        return ""
    w, h, c = params
    root, ext = os.path.splitext(origin)
    return "%s_%dw_%dh_%dc%s"%(root,w,h,c,ext)
    
def cut_image(image, width, height):
    w, h = image.size
    
    new_ratio = height*1.0/width
    old_ratio = h*1.0/w

    if new_ratio > old_ratio:
        new_height = h
        new_width = int(new_height/new_ratio)
    else:
        new_width = w
        new_height = int(new_ratio*new_width)
    l = (w-new_width)/2
    u = (h-new_height)/2
    r = w-l
    b = h-u
    thumbnail = image.crop((l,u,r,b))
    thumbnail.thumbnail((width, height), Image.ANTIALIAS)
    return thumbnail

def deflate_image(image, width, height):
    w, h = image.size

    old_ratio = h*1.0/w

    new_width = width
    new_height = int(width*old_ratio)

    image.thumbnail((new_width, new_height), Image.ANTIALIAS)
    return image

def create_thumbnail(data, params):
    width, height, cut = params
    size = (width, height)
    if not data:
        return data

    f = BytesIO(data)
    p = Image.open(f)

    if cut:
        p = cut_image(p, width, height)
    else:
        p = deflate_image(p, width, height)

    output = BytesIO()
    if p.mode == 'RGBA':
        p.save(output, "PNG")
    else:
        p.save(output, 'JPEG')
    thumbnail = output.getvalue()
    return thumbnail

