#!/usr/bin/python3

# Since Google's switch from Hangouts to Google Chat,
# the endpoints and behaviour of codes has chasnged.
# This should work with the latest version.
#
# Since: 2020-10-01T00:00Z

import sys
from requests import post
from base64 import b64decode
from re import findall
from os import getenv

code = sys.argv[1].lower()
r = post(
    "https://meet.google.com/$rpc/google.rtc.meetings.v1.MeetingSpaceService/ResolveMeetingSpace",
    headers={
        "content-type": "application/x-protobuf",
        "Cookie": getenv('COOKIE'),
        "authorization": getenv('GAPIAUTH'),
        "x-goog-api-key": getenv('GAPIKEY'),
        "x-goog-authuser": getenv('COOKIE_AUTHUSER'),
        "x-goog-encode-response-if-executable": "base64",
        "x-origin": "https://meet.google.com"
    },
    data=(
             "\n%s0" if '-' in code  # meeting code
             else "%s\"CA"  # lookup code
         ) % code
)
print(r)
print(r.status_code)
if r.status_code != 200:
    if r.status_code == 401 and "Request had invalid authentication credentials." in r.text:
        raise Exception("Authentication failed.")
    exit(1)
print(r.text)
ret = b64decode(r.text).strip().split(b'\n')
print(ret)
(spacecode, meetcode, meeturl) = tuple(
    map(
        bytes.decode,
        tuple(
            findall(
                r"^"
                r".*?(spaces\/[A-Za-z0-9\\._]{12})"
                r".*?([a-z]{3}-[a-z]{4}-[a-z]{3})"
                r".*?(\$https?:\/\/(?:\w*\.)?meet\.google\.com\/[\^\-\\\]\_\.\~\!\*\'\(\)\;\:\@\&\=\+\$\,\/\?\%\#A-z0-9]*?)"
                r".*?$"
                    .replace('.*?', '\x13', 1)
                    .replace('.*?', '\x12\x0c', 1)
                    .replace('.*?', '\x1a', 1)
                    .replace('.*?', '\x02\x08\x01', 1)
                    .encode(),
                ret[0]  # First line contains the spacecode, meetcode, and meeturl
            )[0]  # use the one and only result
        )
    )
)
print(spacecode, meetcode, meeturl)
if len(ret) >= 4:
    (lookupcode) = tuple(
        map(
            bytes.decode,
            tuple(
                findall(
                    b"^(.+)\x00$",
                    ret[3]
                )
            )
        )
    )
    print(lookupcode)
