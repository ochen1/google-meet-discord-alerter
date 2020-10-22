#!/usr/bin/python3

# Since Google's switch from Hangouts to Google Chat,
# the endpoints and behaviour of codes has chasnged.
# This should work with the latest version.
#
# Since: 2020-10-01T00:00Z

import sys
from requests import get, post
from urllib.parse import urlparse
from base64 import b64decode
from re import match, findall
from os import getenv


def get_requestdata_template(code):
    idtype = None
    dataformat = None
    if match(r"^([a-z]{3}-[a-z]{4}-[a-z]{3})$", code):
        # Meeting code provided
        idtype = "MEETING_CODE"
        dataformat = "\n\x0c{0}\x30\x01"
    elif match(r"^([a-zA-Z0-9]+)$", code):
        # (likely) Lookup code provided
        idtype = "LOOKUP_CODE"
        dataformat = "{0}\"\x02CA"
    else:
        raise ValueError("Unrecognized identifier.")
    return idtype, dataformat


def validate_meeting_code(code):
    idtype = get_requestdata_template(code)[0]
    if idtype != "LOOKUP_CODE":
        return
    r = get(
        "https://meet.google.com/lookup/%s?authuser=%s" % (code, getenv('COOKIE_AUTHUSER')),
        headers={
            "Cookie": getenv('COOKIE'),
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
        },
        allow_redirects=False
    )
    if r.status_code != 302:
        raise Exception("Meeting code validation returned unexpected %s status code." % r.status_code)
    if urlparse(r.headers['Location']).path.split('/')[1:3] == ['_meet', 'whoops']:
        return False
    else:
        return True


def resolve_meeting_space(code):
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
        data=get_requestdata_template(code)[1].format(code)
    )

    if r.status_code != 200:
        print(repr(r.status_code), repr(r.text))
        if r.status_code == 401 and "Request had invalid authentication credentials." in r.text:
            raise Exception("Authentication failed.")
        if r.status_code == 400 and "Request contains an invalid argument." in r.text:
            raise Exception("Invalid argument.")
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


if __name__ == '__main__':
    try:
        code = sys.argv[1].lower()
    except IndexError:
        exit(1)
    if not validate_meeting_code(code):
        print("Unable to validate lookup code.")
        exit(255)
    else:
        resolve_meeting_space(code)
