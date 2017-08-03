#!/usr/bin/env python
import requests
import sys

if __name__ == '__main__':
    host = 'localhost'
    port = 5150
    try:
        token = sys.argv[1]
    except IndexError:
        sys.exit('Supply a token')
    url = 'http://{}:{}'.format(host, port)
    headers = {'X-Auth-Token': str(token)}
    r = requests.get(url, headers=headers)
    print(r.text)
