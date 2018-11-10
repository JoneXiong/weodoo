# -*- coding: utf-8 -*-
import logging
import time
import random
import json

from odoo import http
from odoo.addons.web.controllers.main import Home, ensure_db
from odoo.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect
import requests
from odoo.http import request



_logger = logging.getLogger(__name__)

QR_DICT = {}


def gen_id(data):
    _now = time.time()
    tm = str(int(_now*100))[-7:]
    for k,v in QR_DICT.items():
        if _now - v['ts'] > 600:
            del QR_DICT[k]
    _id = str(random.randint(1,9)) + tm
    QR_DICT[_id] = {'ts':_now, 'state': 'gen', 'data': data}
    return _id


class SocialLogin(http.Controller):


    @http.route('/corp/bind', type='http', auth="public", website=True)
    def wx_bind(self, **kw):
        qr_id = kw.get('qr_id')
        _info = QR_DICT[qr_id]['data']

        values = request.params.copy()
        values['qr_id'] = qr_id
        values['avatar'] = _info['avatar']
        values['name'] = _info['name']
        request.session['qr_id'] = qr_id
        return request.render('weodoo.wx_bind', values)

