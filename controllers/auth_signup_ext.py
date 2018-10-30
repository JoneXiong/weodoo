# coding=utf-8

import logging

import odoo
from odoo import http
from odoo.http import request
from odoo.addons import auth_signup


_logger = logging.getLogger(__name__)


class AuthSignupHome(auth_signup.controllers.main.AuthSignupHome):
    @http.route()
    def web_login(self, *args, **kw):
        response = super(AuthSignupHome, self).web_login(*args, **kw)
        from .controllers import QR_DICT
        qr_id = request.session.get('qr_id',None)#kw.get('qr_id', False)
        if qr_id and request.params['login_success']:
            from .controllers import QR_DICT
            if qr_id in QR_DICT:
                qr = QR_DICT[qr_id]
                if 1:#qr['state']=='fail' and qr['openid']:
                    user = request.env.user
                    user.write({
                        'oauth_provider_id': qr['data']['oauth_provider_id'],
                        'oauth_uid': qr['data']['user_id'],
                    })
        return response

