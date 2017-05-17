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

username = environ.get('OS_USERNAME')
pauth_args = {
        'user_domain_name': environ.get('OS_USER_DOMAIN_NAME'),
        'project_domain_name': environ.get('OS_PROJECT_DOMAIN_NAME'),
        'project_name': environ.get('OS_PROJECT_NAME'),
        'auth_url': environ.get('OS_AUTH_URL'),
        'password': environ.get('OS_PASSWORD'),
        'username': username,
}

auth_args = pauth_args
plugin = 'v3password'
region = environ.get('OS_REGION_NAME')
endpoint_filter = {
'service_type': 'identity',
'interface': 'admin',
'region_name': region
}

loader = loading.get_plugin_loader(plugin)
auth = loader.load_from_options(**auth_args)
sess = Session(auth=auth)
ks = client.Client(session=sess)
