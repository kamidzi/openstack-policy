#!/usr/bin/env python
from ks_auth import ks
from ks_auth import sess
from ks_auth import trust_auth
from ks_auth import utils
from novaclient import client as nclient
from cinderclient import client as cclient
from novaclient import exceptions
from pprint import pprint
from time import sleep
from utils import *
import sys

VERSION = '2'

def poll_volume(volume, interval=2, limit=4, *args, **kwargs):
    for i in range(0, limit):
        yield cinder.volumes.get(volume.id)
        sleep(interval)


if __name__ == '__main__':
    try:
        instance_id = sys.argv[1]
    except IndexError:
        sys.exit('Supply an instance id')

    nova = nclient.Client(VERSION, session=sess)
    cinder = cclient.Client(VERSION, session=sess)

    def dump_accessinfo():
        for k, v in utils.access_info_vars(sess).iteritems():
            print('* {}: {}'.format(k, v))

    def test():
        extras = {}
        for i, k in enumerate(['project_id', 'user_id'], 1):
            try:
                extras[k] = sys.argv[i]
            except IndexError:
                pass
        vol = {
            'name': 'test-volume',
            'size': 1
        }
        vol.update(extras)
        print('Creating volume')
        vol = cinder.volumes.create(**vol)
        for state in poll_volume(vol, interval=3):
            if str(state.status).lower() == 'available' \
                and hasattr(vol, 'os-vol-tenant-attr:tenant_id'):
                break
        print(render_volume(vol))

        try:
            args = {
                'server_id': instance_id,
                'volume_id': vol.id
            }

            print('Attaching volume')
            attached_vol = nova.volumes.create_server_volume(**args)
            print(render_vol_attachment(attached_vol))
            for state in poll_volume(vol):
                if str(state.status).lower() != 'attaching':
                    break
            # need to unattach first
            args = {
                'attachment_id': attached_vol.id,
                'server_id': instance_id
            }
            nova.volumes.delete_server_volume(**args)
        except Exception, e:
            print('ERROR: %s' % e.message)
        finally:
            print('Deleting volume')
            for state in poll_volume(vol):
                if str(state.status).lower() == 'available':
                    break
            vol.delete()

    print('Initial Auth Info:')
    for authtype, params in utils.initial_auth_info(ks.auth.client.session):
        print(' %s' % authtype)
        print('  %s' % params)
    dump_accessinfo()

    nova = nclient.Client(VERSION, session=sess)
    cinder = cclient.Client(VERSION, session=sess)
    print('Nova API: %s' % nova.api_version)
    test()

    # switch to trust-based auth here
    print('Switching to trust-based auth')
    sess.auth = trust_auth
    dump_accessinfo()
    test()
