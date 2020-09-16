#!/usr/bin/python3

import sys
import time
from os import getenv
from re import match

from requests import get

code = sys.argv[1].lower()

try:
    assert match(r"^[\da-z]{10}$", code)
except AssertionError:
    print("Invalid lookup code.")
    sys.exit(127)

r = get("https://meet.google.com/lookup/%s" % code, headers={
    'user-agent': getenv('CLIENT_USER_AGENT'),
    'cookie': getenv('COOKIE')
}, allow_redirects=False)

try:
    if 'whoops' in r.headers['Location']:
        print('Unable to resolve meeting.')
        sys.exit(1)
    elif not match(r"^https?:\/\/meet\.google\.com\/\w{3}-\w{4}-\w{3}(?:\?authuser=(\d))?$", r.headers['Location']):
        raise KeyError
    else:
        print('Meeting resolved!')
        # print(r.headers['Location'])
        sys.exit(0)
except KeyError:
    print('Error. Perhaps malformed link or improper authentication?')
    sys.exit(3)

sys.exit(10)
