# -*- coding: utf-8 -*-
from flask import request
from flask import g
from flask import Blueprint
from libs.crossdomain import crossdomain
from libs.util import make_response
from libs.response_meta import ResponseMeta
from authorization import require_auth
import requesocks 
import config
import json

app = Blueprint('translator', __name__)

languages = [u'ar', u'bs-Latn', u'bg', u'ca', u'zh-CHS', u'zh-CHT', u'hr', u'cs', u'da', u'nl', u'en', u'et', u'fi', u'fr', u'de', u'el', u'ht', u'he', u'hi', u'mww', u'hu', u'id', u'it', u'ja', u'sw', u'tlh', u'tlh-Qaak', u'ko', u'lv', u'lt', u'ms', u'mt', u'yua', u'no', u'otq', u'fa', u'pl', u'pt', u'ro', u'ru', u'sr-Cyrl', u'sr-Latn', u'sk', u'sl', u'es', u'sv', u'th', u'tr', u'uk', u'ur', u'vi', u'cy']


def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    htmlCodes = (
            ("'", '&#39;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;')
        )
    for code in htmlCodes:
        s = s.replace(code[1], code[0])
    return s


@app.route('/translate', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*', headers=['Authorization'])
@require_auth
def traslate_message():
    text = request.args.get('text')
    lan = request.args.get('to')


    header = request.headers.get('Accept-Language', '')
    locales = [locale.split(';')[0] for locale in header.split(',')]
    accept_lan = locales[0]

    if not lan:
        lan = accept_lan

    if not text or not lan:
        raise ResponseMeta(400, "invalid param")

    if lan in ('zh-Hans-CN','zh-Hans-HK','zh-Hans-MO','zh-Hans-SG','zh-Hans-TW'):
        lan = 'zh-Hans'

    if lan.startswith('en-'):
        lan = 'en'
    if lan.startswith('tr-'):
        lan = 'tr'
    
    USE_MICROSOFT = False
    if USE_MICROSOFT:
        translator = g.translator
        translation = translator.translate(text, lan)
        obj = {"translation":translation}
        return make_response(200, obj)
    else:
        session = requesocks.session()
        session.proxies = {
            'http': config.SOCKS5_PROXY,
            'https': config.SOCKS5_PROXY,
        }

        params = {"key":config.GOOGLE_API_KEY,
                  "q":text,
                  "target":lan}

        url = "https://www.googleapis.com/language/translate/v2"
        resp = session.get(url, params=params)

        if resp.status_code != 200:
            raise ResponseMeta(400, "translate error")

        r = json.loads(resp.content)
        if len(r['data']['translations']) > 0:
            translation = r['data']['translations'][0]['translatedText']
            translation = html_decode(translation)
            obj = {"translation": translation}
            return make_response(200, obj)
        else:
            raise ResponseMeta(400, "translate result is empty")
        

