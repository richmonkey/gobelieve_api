# -*- coding: utf-8 -*-
from flask import request
from flask import g
from flask import Blueprint
from libs.crossdomain import crossdomain
from libs.util import make_response
from libs.response_meta import ResponseMeta
from authorization import require_auth

app = Blueprint('translator', __name__)

languages = [u'ar', u'bs-Latn', u'bg', u'ca', u'zh-CHS', u'zh-CHT', u'hr', u'cs', u'da', u'nl', u'en', u'et', u'fi', u'fr', u'de', u'el', u'ht', u'he', u'hi', u'mww', u'hu', u'id', u'it', u'ja', u'sw', u'tlh', u'tlh-Qaak', u'ko', u'lv', u'lt', u'ms', u'mt', u'yua', u'no', u'otq', u'fa', u'pl', u'pt', u'ro', u'ru', u'sr-Cyrl', u'sr-Latn', u'sk', u'sl', u'es', u'sv', u'th', u'tr', u'uk', u'ur', u'vi', u'cy']

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

    translator = g.translator
    translation = translator.translate(text, lan)
    obj = {"translation":translation}
    return make_response(200, obj)

