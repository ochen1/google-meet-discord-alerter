import sys
from itertools import repeat
from json import loads as loadsJSON
from os import getenv, system
from pprint import pformat
from threading import Thread
from time import gmtime, sleep, strftime, time

import schedule
from flask import Flask, Response
from flask_httpauth import HTTPBasicAuth
from requests import post
from scraper import getNumPeople
from werkzeug.security import check_password_hash

codes = loadsJSON(getenv('CODES'))
out = list(repeat(tuple((None, 0)), len(codes)))

up = time()

app = Flask(__name__)
auth = HTTPBasicAuth()

users = loadsJSON(getenv("PASSWD"))


def runwarning(code):
    post(
        getenv('WEBHOOK'),
        json={
            'content': "<@&%s>\nDisclaimer: This Discord bot by Oliver Chen is provided \"AS IS\". Oliver makes no other warranties, expressive or implied, and hereby disclaims all implied warranties, including any warranty of merchantability and warranty of fitness for a particular purpose." % getenv("EVENT_PING_ID"),
            "embeds": [{
                "title": "Google Meet started!",
                "description": "A Google Meet for your class `%s` resolved!\nThis usually means a teacher has joined the meet!\nHurry and join in ASAP!" % code[0],
                "color": 8977942,
                "timestamp": strftime("%Y-%m-%dT%H:%M:%SZ", gmtime()),
                "footer": {
                    "icon_url": "https://cdn.discordapp.com/avatars/694234706430001222/bc76d00201925b023f550655bea29adc.png",
                    "text": "idontknow#6929"
                },
                "author": {
                    "name": "Google Meet Alerter Bot - Reminder",
                    "url": "https://github.com/ochen1/google-meet-discord-alerter",
                    "icon_url": "https://cdn.discordapp.com/avatars/755506478483374230/115ee7a0c067f5b6f2490207f44af318.png"
                },
                "fields": [
                    {
                        "name": "<:gclassroom:755519374277738536> Google Classroom",
                        "value": "Click [<:gclassroom:755519374277738536> here](https://classroom.google.com/u/0/c/%s) to go to the event Classroom." % code[2],
                        "inline": True
                    },
                    {
                        "name": "<:gmeet:755518059703435357> Google Meet",
                        "value": "Click [<:gmeet:755518059703435357> here](https://meet.google.com/lookup/%s) to enter the meet." % code[1],
                        "inline": True
                    },
                    {
                        "name": ":hash: Meet Details",
                        "value": "Number of people in the meet as of now: %i" % getNumPeople(code[1]),
                        "inline": False
                    },
                    {
                        "name": "Want to contribute?",
                        "value": "[Report an issue/suggestion](https://raw.githack.com/ochen1/google-meet-discord-alerter/master/docs/ticket.html) or email o.chen1@share.epsb.ca to help develop!"
                    }
                ]
            }]
        }
    )


def check():
    global out
    for i, code in enumerate(codes):
        print(code)
        ret = system(' '.join(["./test.py", code[1]]))
        print(ret)
        if ret == 0 and ret != out[i][0]:
            runwarning(code)
        out[i] = tuple((ret, time()))


schedule.every(1).minute.at(':00').do(check)


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


@app.route('/')
@auth.login_required
def index():
    s = f"Program is running.\n\
Current Time: {time()}\n\
Up since: {up}\n\
Uptime: {time() - up}\n\
Codes: {repr(codes)}\n\
Output: {', '.join(map(repr, out))}\n\
Globals:\n{pformat(globals())}\n\
"
    return Response(s, content_type="text/plain")


@app.route('/force')
@auth.login_required
def forceCheck():
    check()
    return "OK!"


if __name__ == "__main__":
    webThread = Thread(target=app.run, kwargs={
        'host': "0.0.0.0", 
        'port': getenv('PORT')
    })
    webThread.daemon = True
    webThread.start()
    while True:
        schedule.run_pending()
        sleep(1)
    sys.exit()
