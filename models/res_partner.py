# coding=utf-8
import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):

    _inherit = 'res.partner'


    wecorp_notify = fields.Boolean('接收企业微信通知', default=True)


    @api.multi
    def _notify(self, message, force_send=False, send_after_commit=True, user_signature=True):
        res = super(ResPartner, self)._notify(message, force_send, send_after_commit, user_signature)
        self._notify_by_weodoo(message)
        return res

    @api.multi
    def _notify_by_weodoo(self, message):
        _logger.info('>>> _notify_by_weodoo: %s'%str(message))
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for partner in self:
            if partner.get_corp_key() and partner.wecorp_notify and partner.im_status!='1online':
                _logger.info('>>> notify by weodoo: %s'%str((message,partner)))
                _body = message.body.replace('<p>','').replace('</p>','')
                _content = u'%s\n%s'%(message.subject, _body) if message.subject else _body
                _head = u'%s 发送到 %s'%(message.author_id.name, message.record_name)
                try:
                    message_content = u'%s：%s'%(_head,_content)
                    partner.send_corp_msg({"mtype": "card", "title": _head, 'description': _content, 'url': '%s/mail/view?message_id=%s'%(base_url, message.id)})
                except:
                    import traceback;traceback.print_exc()

    def send_corp_msg(self, msg):
        from ..rpc import send_msg
        send_msg(self.env, [self.user_ids[0].oauth_uid], msg)

    def get_corp_key(self):
        return self.user_ids[0].oauth_uid
