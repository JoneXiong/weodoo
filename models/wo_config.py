# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WeOdooConfig(models.Model):

    _name = 'wo.config'
    _description = u'WeOdoo设置'

    oauth_client_key = fields.Char('授权应用Key')
    oauth_client_secret = fields.Char('授权应用Secret')
    enable_wx_notify = fields.Boolean('启用企业微信通知', default=True)

    @api.multi
    def name_get(self):
        return [(obj.id, "WeOdoo 设置") for obj in self]


    @api.multi
    def write(self, vals):
        if "oauth_client_key" in vals:
            vals["oauth_client_key"] = vals["oauth_client_key"].lstrip().rstrip()
        result = super(WeOdooConfig, self).write(vals)
        third_provider = self.env.ref('weodoo.provider_third')
        if "oauth_client_key" in vals:
            third_provider.write({"client_id": vals["oauth_client_key"]})
        return result
