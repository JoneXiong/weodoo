# coding=utf-8
import werkzeug
import json
try:
    import urlparse
except:
    from urllib.parse import urlparse
try:
    import urllib2
except:
    from urllib import request as urllib2

import logging

from odoo import http
from odoo.http import request
from odoo.addons.auth_oauth.controllers.main import OAuthController, fragment_to_query_string
from odoo.addons.auth_oauth.controllers.main import OAuthLogin

from odoo.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect
from odoo import registry as registry_get
from odoo import api, http, SUPERUSER_ID, _

from odoo.exceptions import AccessDenied
from odoo.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)


class OAuthControllerExt(OAuthController):

    #@http.route()
    @http.route('/auth_oauth/signin3rd', type='http', auth='none')
    @fragment_to_query_string
    def signin_3rd(self, **kw):
        state = json.loads(kw['state'])
        dbname = state['d']
        provider = state['p']
        context = state.get('c', {})
        registry = registry_get(dbname)
        with registry.cursor() as cr:
            try:
                env = api.Environment(cr, SUPERUSER_ID, context)
                credentials = env['res.users'].sudo().auth_oauth_third(provider, kw)
                cr.commit()
                action = state.get('a')
                menu = state.get('m')
                redirect = werkzeug.url_unquote_plus(state['r']) if state.get('r') else False
                url = '/web'
                if redirect:
                    url = redirect
                elif action:
                    url = '/web#action=%s' % action
                elif menu:
                    url = '/web#menu_id=%s' % menu
                if credentials[0]==-1:
                    from .controllers import gen_id
                    credentials[1]['oauth_provider_id'] = provider
                    qr_id = gen_id(credentials[1])
                    url = '/corp/bind?qr_id=%s'%qr_id
                else:
                    return login_and_redirect(*credentials, redirect_url=url)
            except AttributeError:
                import traceback;traceback.print_exc()
                # auth_signup is not installed
                _logger.error("auth_signup not installed on database %s: oauth sign up cancelled." % (dbname,))
                url = "/web/login?oauth_error=1"
            except AccessDenied:
                import traceback;traceback.print_exc()
                # oauth credentials not valid, user could be on a temporary session
                _logger.info('OAuth2: access denied, redirect to main page in case a valid session exists, without setting cookies')
                url = "/web/login?oauth_error=3"
                redirect = werkzeug.utils.redirect(url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            except Exception as e:
                # signup error
                _logger.exception("OAuth2: %s" % str(e))
                url = "/web/login?oauth_error=2"

        return set_cookie_and_redirect(url)

class OAuthLoginExt(OAuthLogin):

    def list_providers(self):
        third_provider_id = request.env.ref('weodoo.provider_third').id
        try:
            providers = request.env['auth.oauth.provider'].sudo().search_read([('id', '=', third_provider_id)])
        except Exception:
            providers = []
        for provider in providers:
            return_url = request.httprequest.url_root + 'auth_oauth/signin3rd'
            state = self.get_state(provider)
            params = dict(
                response_type='token',
                client_id=provider['client_id'],
                redirect_uri=return_url,
                scope=provider['scope'],
                state=json.dumps(state),
            )
            provider['auth_link'] = "%s?%s" % (provider['auth_endpoint'], werkzeug.url_encode(params))
        return providers
