# -*- coding: utf-8 -*-
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

from odoo import models, fields, api
from odoo.exceptions import AccessDenied


_logger = logging.getLogger(__name__)

class ResUsers(models.Model):

    _inherit = 'res.users'


    @api.model
    def _auth_oauth_signin_third(self, provider, validation, params):
        oauth_user = self.search([("oauth_uid", "=", validation['user_id']), ('oauth_provider_id', '=', provider)])
        if not oauth_user:
            return -1
        else:
            return self._auth_oauth_signin(provider, validation, params)

    @api.model
    def auth_oauth_third(self, provider, params):
        # Advice by Google (to avoid Confused Deputy Problem)
        # if validation.audience != OUR_CLIENT_ID:
        #   abort()            
        # else:
        #   continue with the process   
        access_token = params.get('access_token')
        validation = self._auth_oauth_validate(provider, access_token)
        # required check       
        if not validation.get('user_id'):
            # Workaround: facebook does not send 'user_id' in Open Graph Api
            if validation.get('id'):
                validation['user_id'] = validation['id']
            else:
                raise AccessDenied()

        # retrieve and sign in user     
        login = self._auth_oauth_signin_third(provider, validation, params)
        if login==-1:
            return login, validation
        if not login:
            raise AccessDenied()
        # return user credentials       
        return (self.env.cr.dbname, login, access_token)


    def is_available(self):
        return self.oauth_uid or super(ResUsers, self).is_available()

    def send_corp_text(self, text):
        msg = {
            "mtype": "text",
            "content": text,
        }
        self.partner_id.send_corp_msg(msg)

    @api.multi
    def send_corp_text_confirm(self):
        self.ensure_one()

        new_context = dict(self._context) or {}
        new_context['default_model'] = 'res.users'
        new_context['default_method'] = 'send_corp_text'
        new_context['record_ids'] = self.id
        return {
            'name': u'发送企业微信消息',
            'type': 'ir.actions.act_window',
            'res_model': 'wo.confirm',
            'res_id': None,
            'view_mode': 'form',
            'view_type': 'form',
            'context': new_context,
            'view_id': self.env.ref('weodoo.wo_confirm_view_form_send').id,
            'target': 'new'
        }
