# coding=utf-8

import logging
import werkzeug
import werkzeug.utils


from odoo import http
from odoo.http import request
from odoo.addons.mail.controllers.main import MailController

_logger = logging.getLogger(__name__)


class MailControllerExt(MailController):

    @http.route()
    def mail_action_view(self, **kwargs):
        _logger.info('>>> %s'%request.httprequest.url)
        _logger.info('>>>mail_action_view %s'%kwargs)
        if not request.session.uid:
            # X2Z0eXBlPXdv
            return werkzeug.utils.redirect('/web/login?_fm=X2Z0eXBlPXdv&redirect=%s'%werkzeug.url_quote_plus(request.httprequest.url), 303)
        res = super(MailControllerExt, self).mail_action_view(**kwargs)
        return res
