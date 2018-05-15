#!/usr/bin/env python
from keystoneauth1 import loading
from keystoneclient import client
from keystoneauth1.session import Session
from os import environ
import os
try:
    import simplejson as json
except ImportError:
    import json


def build_auth_args():
    prefixes = ['user_domain', 'project_domain', 'project']
    suffixes = ('_id', '_name')
    _args = {}
    # prefer *_id over *_name equivalent as mutually exclusive opts
    for p in prefixes:
        for s in suffixes:
            key = ''.join([p, s])
            envvar = ('_'.join(['os', key])).upper()
            value = environ.get(envvar)
            if value:
                _args[key] = value
                break

    _args.update({
        'auth_url': environ.get('OS_AUTH_URL'),
        'password': environ.get('OS_PASSWORD'),
        'username': environ.get('OS_USERNAME')
    })
    return _args


_auth_args = build_auth_args()
_plugin = 'v3password'
region = environ.get('OS_REGION_NAME')
endpoint_filter = {
    'service_type': 'identity',
    'interface': 'admin',
    'region_name': region
}

loader = loading.get_plugin_loader(_plugin)
auth = loader.load_from_options(**_auth_args)
sess = Session(auth=auth, verify=environ.get('OS_CACERT'))
ks = client.Client(session=sess)
