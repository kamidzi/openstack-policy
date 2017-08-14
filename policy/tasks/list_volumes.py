#!/usr/bin/env python
from ks_auth import sess
from novaclient import client as nclient
from cinderclient import client as cclient

version = 2
nova = nclient.Client(version, session=sess)
cinder = cclient.Client(version, session=sess)
print('Nova API: %s' % nova.api_version)
print('Using novaclient:')
try:
    print(nova.volumes.list())
except AttributeError:
    print([])
print('Using cinderclient:')
print(cinder.volumes.list())
