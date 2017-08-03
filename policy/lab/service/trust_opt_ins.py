#!/usr/bin/env python

from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneclient import client as ks_client
from keystonemiddleware import auth_token
from oslo_config import cfg
from wsgiref import simple_server
import json
import logging
import os
import sys
import webob.dec

CONF = cfg.CONF
CONF(project='trust_service')
loading.session.register_conf_options(cfg.CONF, 'communication')
vars = filter(lambda x: x[0].startswith('OS_'), os.environ.iteritems())
conf_keys = CONF.keys()
for k, v in vars:
# Try the full var first
    n = k.lower()
    cands = (n, n[3:])
    for var in cands:
        if var in conf_keys:
            self.conf.set_default(name=var, default=v)
            break

CONF(sys.argv[1:])
GROUP = 'service_auth'

loading.conf.register_conf_options(CONF, GROUP)
# MUST use 'auth_section'
try:
    auth = loading.conf.load_from_conf_options(CONF, GROUP)
except AttributeError, e:
    sys.exit('Configuration error: %s' % e)
except Exception, e:
    sys.exit('Unhandled exception: %s - %s' % (type(e), e.message))

# Initial session is for service user
SESSION = session.Session(auth=auth)

def list_trusts(req):
    auth = req.environ['keystone.token_auth']
    ks = ks_client.Client('3', session=SESSION, auth=auth)
    user_id = ks.auth.client.get_user_id()
    user_type = ['trustor', 'trustee'] 

    def render_trust(trust):
        return trust._info

    ret = {}
    for t in user_type:
        key = 'as_' + t
        args = {}
        name = '%s_user' % t
        args[name] = user_id
        ret[key] = map(render_trust, ks.trusts.list(**args))
    return  {'trusts': ret}

@webob.dec.wsgify
def app(req):
    resp = list_trusts(req)
    return webob.Response(json.dumps(resp))

PORT = 5150
if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger(cfg.CONF.project)

    app = auth_token.AuthProtocol(app,{})
    server = simple_server.make_server('', PORT, app)
    server.handle_request()
    #server.serve_forever()
