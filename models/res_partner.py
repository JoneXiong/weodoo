# coding=utf-8

from openerp import models, fields, api


class res_partner(models.Model):

    _inherit = 'res.partner'


    def send_corp_msg(self, msg):
        from ..rpc import send_msg
        send_msg(self.env, self.user_ids[0].oauth_uid, msg)

    def get_corp_key(self):
        return self.user_ids[0].oauth_uid
