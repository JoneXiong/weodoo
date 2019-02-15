# coding=utf-8

import logging
import werkzeug.utils
import werkzeug
import base64
import json

import odoo
from odoo import http
from odoo.http import request
from odoo.addons import auth_signup
from odoo.addons.auth_oauth.controllers.main import OAuthLogin


_logger = logging.getLogger(__name__)


class AuthSignupHome(OAuthLogin):

    def _deal_state_r(self, state):
        _logger.info('>>> get_state %s'%request.httprequest.url)
        _fm = request.params.get('_fm', None)
        if _fm:
            fragment = base64.urlsafe_b64decode(_fm.encode('utf-8')).decode('utf-8')
            r = werkzeug.url_unquote_plus(state.get('r', ''))
            state['r'] = werkzeug.url_quote_plus('%s#%s'%(r, fragment))
        return state

    def _get_auth_link_wo(self, provider=None):
        if not provider:
            provider = request.env(user=1).ref('weodoo.provider_third')

        return_url = request.httprequest.url_root + 'auth_oauth/signin3rd'
        state = self.get_state(provider)
        self._deal_state_r(state)
        params = dict(
            response_type='token',
            client_id=provider['client_id'],
            redirect_uri=return_url,
            scope=provider['scope'],
            state=json.dumps(state),
        )
        return "%s?%s" % (provider['auth_endpoint'], werkzeug.url_encode(params))

    def list_providers(self):
        providers = super(AuthSignupHome, self).list_providers()
        weodoo_provider = request.env(user=1).ref('weodoo.provider_third')
        for provider in providers:
            if provider['id']==weodoo_provider.id:
                provider['auth_link'] = self._get_auth_link_wo(provider)
                break
        return providers


    @http.route()
    def web_login(self, *args, **kw):
        if request.httprequest.method == 'GET':
            if request.session.uid and request.params.get('redirect'):
                return http.redirect_with_hash(request.params.get('redirect'))
            fm = request.params.get('_fm', None)
            if not request.session.uid and fm!=None:
                fragment = base64.urlsafe_b64decode(fm.encode('utf-8')).decode('utf-8')
                if '_ftype=wo' in fragment:
                    auth_link = self._get_auth_link_wo()
                    return werkzeug.utils.redirect(auth_link, 303)

        response = super(AuthSignupHome, self).web_login(*args, **kw)

        from .controllers import QR_DICT
        qr_id = str(request.session.get('qr_id', ''))#kw.get('qr_id', False)
        if qr_id and (request.params['login_success'] or request.session.uid):
            from .controllers import QR_DICT
            if qr_id in QR_DICT:
                qr = QR_DICT[qr_id]
                if 1:#qr['state']=='fail' and qr['openid']:
                    # 绑定当前登录的用户
                    if request.session.uid:
                        user = request.env["res.users"].sudo().search(([('id','=',request.session.uid)]))
                    else:
                        user = request.env.user
                    user.write({
                        'oauth_provider_id': qr['data']['oauth_provider_id'],
                        'oauth_uid': qr['data']['user_id'],
                    })
                    request.env.cr.commit()

        return response

    @http.route()
    def web_client(self, s_action=None, **kw):
        res = super(AuthSignupHome, self).web_client(s_action, **kw)
        if not request.session.uid:
            fm = request.params.get('_fm', None)
            if fm!=None:
                res = werkzeug.utils.redirect('/web/login?_fm=%s'%fm, 303)
        return res
