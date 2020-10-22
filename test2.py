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
             "\n\x0c%s\x30\x01" if '-' in code  # meeting code
             else "%s\"\x02CA"  # lookup code
         ) % code
)

if r.status_code != 200:
    print(repr(r.status_code), repr(r.text))
    if r.status_code == 401 and "Request had invalid authentication credentials." in r.text:
        raise Exception("Authentication failed.")
    exit(1)
ret = b64decode(r.text).strip().split(b'\n')
(spacecode, meetcode, meeturl) = tuple(
    map(
        bytes.decode,
        tuple(
            findall(
                r"^"                                    # The beginning of the line
                r".*?(spaces\/[A-Za-z0-9\\._]{12})"     # Group 1: The space code that uses base64
                r".*?([a-z]{3}-[a-z]{4}-[a-z]{3})"      # Group 2: The Meet code, using the format xxx-xxxx-xxx
                r".*?(\$"                               # Group 3: The resolved URL for the Meet (starts with $) 
                r"https?:\/\/(?:\w*\.)?"                # Protocol and subdomain, if one exists
                r"meet\.google\.com\/"                  # Hostname (domain), which must be meet.google.com
                r"[\^\-\\\]\_\.\~\!\*\'\(\)\;\:\@\&\=\+\$\,\/\?\%\#A-z0-9]*?)" # Valid characters in URL path
                r".*?$"
                    .replace('.*?', '\x13', 1)          # Replace the .*s in the regex with the proper separators
                    .replace('.*?', '\x12\x0c', 1)
                    .replace('.*?', '\x1a', 1)
                    .replace('.*?', '\x02\x08', 1)
                    .encode(),
                ret[0]  # First line contains the spacecode, meetcode, and meeturl
                    .rstrip(b'\x01')  # Remove the end-of-message byte/character
            )[0]    # Use the one and only result
        )
    )
)
print(spacecode, meetcode, meeturl, sep='\n')
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
