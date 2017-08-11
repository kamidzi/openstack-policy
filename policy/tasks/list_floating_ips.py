#!/usr/bin/env python
from ka_auth import sess
from novaclient import client
from pbr.version import SemanticVersion
from pbr.version import VersionInfo
import keystoneclient.exceptions
import os
import sys
try:
    import simplejson as json
except ImportError:
    import json


MAX_SEMVER = SemanticVersion(major=7, minor=1, patch=2)
semver = VersionInfo('python-novaclient').semantic_version()


version = 2
nova = client.Client(version, session=sess)
print('Nova API: %s' % nova.api_version)

# floating_ips module deprecated as of python-novaclient >= 8.0.0
if semver <= MAX_SEMVER:
    ip_list = nova.floating_ips.list()
    print(ip_list)
else:
    endpoint_filter = {
        'service_type': 'compute',
        'interface': 'public',
        # TODO(kamidzi): may break??
        'region_name': os.environ.get('OS_REGION'),
    }
    try:
        #https://developer.openstack.org/api-ref/compute/#floating-ips-os-floating-ips-deprecated
        resp = sess.get('/os-floating-ips',
                        endpoint_filter=endpoint_filter)
        print(json.dumps(resp.json(), indent=2))
    except keystoneclient.exceptions.NotFound:
        pass
