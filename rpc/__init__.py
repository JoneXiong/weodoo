# coding=utf-8
import logging
import requests

_logger = logging.getLogger(__name__)


oauth_client_cache = {}

def send_msg(env, slug, msg):
    if env.cr.dbname not in oauth_client_cache:
        obj = env.ref('weodoo.weodoo_config_default')
        oauth_client_cache[env.cr.dbname] = {
            "id": obj.id,
            "oauth_key": obj.oauth_client_key,
            "oauth_secret": obj.oauth_client_secret,
        }
    oauth_client = oauth_client_cache[env.cr.dbname]

    mtype = msg["mtype"]
    if mtype=="text":
        data = {
            "oauth_key": oauth_client["oauth_key"],
            "oauth_secret": oauth_client["oauth_secret"],
            "slug": slug,
            "content": msg["content"],
        }
        url = "https://i.calluu.cn/auth3rd/send_text"
        ret = requests.post(url, data)
        _logger.info(ret)
    elif mtype=='image':
        pass
    elif mtype=='voice':
        pass
