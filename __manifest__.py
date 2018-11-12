# -*- coding: utf-8 -*-
{
    'name': "WeOdoo",
    'summary': """企业微信快捷使用，免对接""",
    'description': """""",
    'author': 'Oejia',
    'website': 'http://www.oejia.net/',
    'category': '',
    'version': '0.1',
    'depends': ['auth_oauth'],
    'application': True,
    'data': [
        'views/wx_login.xml',
        'data/oauth_provider.xml',
        'views/wo_config_views.xml',
        'views/wo_confirm_views.xml',
        'views/res_users_views.xml',
    ],
    'qweb': [],
    'demo': [],
}
