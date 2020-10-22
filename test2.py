#!/usr/bin/python3
import sys
from requests import post
from base64 import b64decode
from re import findall

code = sys.argv[1].lower()
r = post(
    "https://meet.google.com/$rpc/google.rtc.meetings.v1.MeetingSpaceService/ResolveMeetingSpace",
    headers={
        "content-type": "application/x-protobuf",
        "Cookie": "<removed>",
        "authorization": "<removed>",
        "x-goog-api-key": "<removed>",
        "x-goog-authuser": "0",
        "x-goog-encode-response-if-executable": "base64",
        "x-origin": "https://meet.google.com"
    },
    data=("\n%s0" if '-' in code # meeting code
                    else "%s\"CA" # lookup code
    ) % code
)
print(r)
print(r.status_code)
print(r.text)
ret = b64decode(r.text).strip().split(b'\n')
print(ret)
(spacecode, meetcode, meeturl) = tuple(map(bytes.decode, tuple(findall(b"^\x13(spaces/[A-Za-z0-9\\._]{12})\x12\x0c([a-z]{3}-[a-z]{4}-[a-z]{3})\x1a(\\$https?://(?:\\w*\\.)?meet\\.google\\.com/[\\^\\-\\]_.~!*'();:@&=+$,/?%#[A-z0-9]*?)2.*$", ret[0])[0])))
print(spacecode, meetcode, meeturl)
(lookupcode) = tuple(map(bytes.decode, tuple(findall(b"^(.+)\x00$", ret[3]))))
print(lookupcode)

# print(b64decode(r.text).decode())
# parsed = b64decode(r.text).decode()
# parsed = parsed.strip()
# parsed = parsed.lstrip("\x13")
# spacecode, parsed = parsed.split("\x12")
# parsed = parsed.lstrip("\x0c")
# roomcode = parsed.split("\x1a")[0]
# url = parsed.split("\x1a")[1].lstrip("$")
# print(spacecode, roomcode, url)
