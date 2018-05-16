#!/usr/bin/env python2
from __future__ import print_function
from ka_auth import ks, auth, sess
from pprint import pprint
try:
    import simplejson as json
except ImportError:
    import json
import cinderclient
import re
import requests
from urlparse import urlsplit
# This import is non-ideal...
from keystoneauth1.access.service_catalog import ServiceCatalogV3


def self(): pass


self.logger = self
self.logger.info = self.logger.debug = self.logger.error = print


def _detect_cinder_api_version(interface='admin'):
    """Detects the highest possible Cinder API version."""
    # Unfortunately, for legacy compat, cannot use any of following:
    #   - keystoneauth1.session.Session#get_all_version_data
    #   - cinderclient.api_versions
    _catalog_cls = ServiceCatalogV3
    ret = 0.0

    try:
        catalog = sess.auth.auth_ref.service_catalog
        if not catalog:
            raise ValueError('auth_ref.catalog')
    except ValueError:
        catalog = _catalog_cls.from_token(sess.auth.auth_ref._data)
        # Last option would be something like this:
        # No convenience methods though
        # endpoint_filter = dict(
        #   service_type='identity',
        #   interface=interface
        # )
        # _catalog = sess.get('/auth/catalog',
        #                     endpoint_filter=endpoint_filter).json()
        # catalog = _catalog_cls(_catalog)

    stypes = ('volumev3', 'volumev2', 'volume')
    _kwargs = dict(interface=interface)
    urls = ()
    for s in stypes:
        _kwargs.update({'service_type': s})
        urls = catalog.get_urls(**_kwargs)
        if urls:
            break

    o = urlsplit(urls[0])
    endpoint = '://'.join([o.scheme, o.netloc])

    try:
        self.logger.info('Detecting API version..')
        resp = requests.get(endpoint)
        verinfo = resp.json()
        # {
        #   "versions": [
        #    {
        #       "status": "CURRENT",
        #       "updated": "2016-02-08T12:20:21Z",
        #       "links": [
        #         {
        #           "href": "http://docs.openstack.org/",
        #           "type": "text/html",
        #           "rel": "describedby"
        #         },
        #         {
        #           "href": "http://openstack.bcpc.example.com:8776/v3/",
        #           "rel": "self"
        #         }
        #       ],
        #       "min_version": "3.0",
        #       "version": "3.0",
        #       "media-types": [
        #         {
        #           "base": "application/json",
        #           "type": "application/vnd.openstack.volume+json;version=1"
        #         },
        #         {
        #           "base": "application/xml",
        #           "type": "application/vnd.openstack.volume+xml;version=1"
        #         }
        #       ],
        #       "id": "v3.0"
        #     }
        #   ]
        # }
        current = list(filter(
            lambda x: x.get('status') == 'CURRENT', verinfo.get('versions')
        )).pop()
        v = current.get('id')
        ret = float(re.sub(r'^v', '', v))
    except Exception as x:
        self.logger.debug(str(x))
        self.logger.error('Failed to auto-detect API version from url {}'
                          ''.format(endpoint))
    return ret


if __name__ == '__main__':
    ver = _detect_cinder_api_version()
    print(ver)
