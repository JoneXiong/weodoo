# coding=utf-8

import logging
import werkzeug.utils

import odoo
from odoo import http
from odoo.http import request
from odoo.addons import auth_signup


_logger = logging.getLogger(__name__)


class AuthSignupHome(auth_signup.controllers.main.AuthSignupHome):
    @http.route()
    def web_login(self, *args, **kw):
        if request.httprequest.method == 'GET':
            if request.session.uid and request.params.get('redirect'):
                return http.redirect_with_hash(request.params.get('redirect'))
            fm = request.params.get('_fm', None)
            if not request.session.uid and fm:
                providers = self.list_providers()
                if providers:
                    return werkzeug.utils.redirect(providers[0]['auth_link'], 303)

        response = super(AuthSignupHome, self).web_login(*args, **kw)

        from .controllers import QR_DICT
        qr_id = request.session.get('qr_id',None)#kw.get('qr_id', False)
        if qr_id and (request.params['login_success'] or request.session.uid):
            from .controllers import QR_DICT
            if qr_id in QR_DICT:
                qr = QR_DICT[qr_id]
                if 1:#qr['state']=='fail' and qr['openid']:
                    if request.session.uid:
                        user = request.env["res.users"].sudo().search(([('id','=',request.session.uid)]))
                    else:
                        user = request.env.user
                    user.write({
                        'oauth_provider_id': qr['data']['oauth_provider_id'],
                        'oauth_uid': qr['data']['user_id'],
                    })
                    request.env.cr.commit()
                    if request.session.uid:
                        return http.redirect_with_hash("/")
        return response

