import sys
from datetime import timedelta
from itertools import repeat
from json import loads as loadsJSON
from os import getenv, popen, WEXITSTATUS
from os.path import abspath, dirname
from pprint import pformat
from threading import Thread
from time import gmtime, sleep, strftime, time

from flask import Flask, Response
from flask_httpauth import HTTPBasicAuth
from requests import post
from werkzeug.security import check_password_hash

codes = loadsJSON(getenv('CODES'))
out = list(repeat([None, 0], len(codes)))

up = time()

app = Flask(__name__)
auth = HTTPBasicAuth()

users = loadsJSON(getenv("PASSWD"))
admins = loadsJSON(getenv("ADMINS"))

skip = loadsJSON(getenv("SKIP"))

scriptdir = dirname(abspath(__file__)).rstrip('/') + '/'


def runwarning(parsed):
    meetcode = parsed.get('meetcode')
    if meetcode:
        meetcode = meetcode.split('-')
        meetcode[1] = ''.join(repeat('\\*', len(meetcode[1])))
        meetcode = '-'.join(meetcode)
    meetcode = str(meetcode)
    meetingspace = str(parsed.get('spacecode').split('/')[1])
    meetingspacelen = len(meetingspace)
    meetingspace = meetingspace[0:meetingspacelen // 2] + \
                   ''.join(repeat('\\*', meetingspacelen - (meetingspacelen // 2)))

    # TODO: Use cards for more data + visually pleasing format
    if getenv('GCHATWEBHOOK', False):
        print("https://chat.googleapis.com/v1/%s/messages?%s" % (getenv('GCHATSPACE'), getenv('GCHATWEBHOOK')))
        print(post(
            "https://chat.googleapis.com/v1/%s/messages?%s" % (getenv('GCHATSPACE'), getenv('GCHATWEBHOOK')),
            json={
                'thread': {
                    'name': '/'.join([getenv('GCHATSPACE'), getenv('GCHATTHREAD')])
                },
                'text': """<users/all> *{classname}*
A <https://meet.google.com/{meetpath}|Google Meet> has resolved! This usually means a teacher joined the meet.
You can also check the the <https://classroom.google.com/c/{classcode}|Google Classroom for this course>.
""".format(
                    classname=parsed['classname'],
                    classcode=parsed['classcode'],
                    meetpath='/'.join(['lookup' if '-' not in parsed['input'] else '_meet', parsed['input']])
                ),
                'cards': [
                    {
                        'header': {
                            'title': "GMDA - Chat Alerts",
                            'subtitle': "by Oliver Chen EPSB/GVH/G9",
                            'imageStyle': "AVATAR",
                            'imageUrl': "https://www.gstatic.com/images/branding/product/2x/hh_chat_64dp.png"
                        },
                        'sections': [
                            {
                                'header': 'Google Meet',
                                'widgets': [
                                    {
                                        'keyValue': {
                                            'topLabel': 'Meet ID',
                                            'content': '/'.join(['lookup' if '-' not in parsed['input'] else '_meet', parsed['input']]),
                                            'contentMultiline': False,
                                            'iconUrl': 'https://www.gstatic.com/images/branding/product/2x/hh_meet_64dp.png'
                                        },
                                        'buttons': [
                                            {
                                                'textButton': {
                                                    'text': "OPEN MEET",
                                                    'onClick': {
                                                        'openLink': {
                                                            'url': '/'.join([
                                                                'https://meet.google.com',
                                                                'lookup' if '-' not in parsed['input'] else '_meet',
                                                                parsed['input']
                                                            ])
                                                        }
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                'header': 'Google Classroom',
                                'widgets': [
                                    {
                                        'keyValue': {
                                            'topLabel': 'Classroom Subject',
                                            'content': parsed['classname'],
                                            'contentMultiline': False,
                                            'iconUrl': 'https://www.gstatic.com/images/branding/product/2x/classroom_64dp.png'
                                        },
                                        'buttons': [
                                            {
                                                'textButton': {
                                                    'text': "OPEN CLASSROOM",
                                                    'onClick': {
                                                        'openLink': {
                                                            'url': '/'.join(['https://classroom.google.com/c',
                                                                             parsed['classcode']])
                                                        }
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                'widgets': [
                                    {
                                        'keyValue': {
                                            'topLabel': 'Timestamp',
                                            'content': strftime("%Y-%m-%d %H:%M:%S GMT", gmtime()),
                                            'contentMultiline': False,
                                            'onClick': {
                                                'openLink': {
                                                    'url': 'https://time.is/UTC'
                                                }
                                            },
                                            'icon': 'CLOCK'
                                        }
                                    }
                                ]
                            },
                            {
                                'header': 'Join us on Discord!',
                                'widgets': [
                                    {
                                        'buttons': [
                                            {
                                                'imageButton': {
                                                    'onClick': {
                                                        'openLink': {
                                                            'url': getenv('DISCORDINV', 'https://discord.gg/')
                                                        }
                                                    },
                                                    'name': 'Discord Invite',
                                                    'iconUrl': 'https://discord.com/assets/2c21aeda16de354ba5334551a883b481.png'
                                                }
                                            },
                                            {
                                                'textButton': {
                                                    'text': 'GET INVITE',
                                                    'onClick': {
                                                        'openLink': {
                                                            'url': getenv('DISCORDINV', 'https://discord.gg/')
                                                        }
                                                    }
                                                }
                                            },
                                            {
                                                'textButton': {
                                                    'text': 'REGISTER',
                                                    'onClick': {
                                                        'openLink': {
                                                            'url': 'https://discord.com/register'
                                                        }
                                                    }
                                                }
                                            }
                                        ],
                                        'textParagraph': {
                                            'text': "Google Meet end alerts, additional Meet verification, dev tools, "
                                                    "and fault explanations are only available on the Discord server."
                                        }
                                    }
                                ]
                            },
                            {
                                'widgets': [
                                    {
                                        'textParagraph': {
                                            'text': "<font color=\"#888888\">This service provided by Oliver Chen is "
                                                    "provided \"AS IS\". Oliver makes no other warranties, "
                                                    "expressive or implied, and hereby disclaims all implied "
                                                    "warranties, including any warranty of merchantability and "
                                                    "warranty of fitness for a particular purpose. v9.6.0</font>"
                                        }
                                    }
                                ]
                            }
                        ],
                        'cardActions': []
                    }
                ]
            }
        ).text)

    post(
        getenv('WEBHOOK'),
        json={
            'content': "<@&%s>\nDisclaimer: Google Meet Discord Alerter by Oliver Chen is provided \"AS IS\". Oliver "
                       "makes no other warranties, expressive or implied, and hereby disclaims all implied "
                       "warranties, including any warranty of merchantability and warranty of fitness for a "
                       "particular purpose." % getenv("EVENT_PING_ID"),
            "embeds": [{
                "title": "Google Meet started!",
                "description": "A Google Meet for your class `%s` resolved!\nThis usually means a teacher has joined the meet!\nHurry and join in ASAP!" %
                               parsed['classname'],
                "color": 8977942,
                "timestamp": strftime("%Y-%m-%dT%H:%M:%SZ", gmtime()),
                "footer": {
                    "icon_url": "https://cdn.discordapp.com/avatars/694234706430001222/65e0958748317bbf206260acd6dba539.png",
                    "text": "idontknow#8950"
                },
                "author": {
                    "name": "Google Meet Alerter Bot - Reminder",
                    "url": "https://github.com/ochen1/google-meet-discord-alerter",
                    "icon_url": "https://cdn.discordapp.com/avatars/755506478483374230/115ee7a0c067f5b6f2490207f44af318.png"
                },
                "fields": [
                    {
                        "name": "<:gclassroom:836629105213571134> Google Classroom",
                        "value": "Click [<:gclassroom:836629105213571134> here](https://classroom.google.com/c/%s) to go to the event Classroom." %
                                 parsed['classcode'],
                        "inline": False
                    },
                    {
                        "name": "<:gmeet:836629017774915625> Google Meet",
                        "value": "Click [<:gmeet:836629017774915625> here](https://meet.google.com/%s%s) to enter the meet." %
                                 ('lookup/' if '-' not in parsed['input'] else '_meet/', parsed['input']),
                        "inline": False
                    },
                    {
                        "name": ":school: Organization",
                        "value": parsed.get('organization', 'none'),
                        "inline": True
                    },
                    {
                        "name": ":1234: Max Meet Size",
                        "value": parsed.get('maxmeetsize', 'none'),
                        "inline": True
                    },
                    {
                        "name": "\u200B",
                        "value": "\u200B",
                        "inline": False
                    },
                    {
                        "name": ":technologist: Developer Info",
                        "value": "Fields below this one should be used with caution, if used at all.\n"
                                 "The intention of these fields is to help developers debug their code.",
                        "inline": False
                    },
                    {
                        "name": ":spy: Verify Your Meet",
                        "value": "The meeting code we've resolved for this code is: %s" % meetcode,
                        "inline": True
                    },
                    {
                        "name": ":spy: Verify Your Meeting Space",
                        "value": "The meeting space we've resolved for this code is: spaces/%s" % meetingspace,
                        "inline": True
                    },
                    {
                        "name": "Want to contribute?",
                        "value": "[Report an issue/suggestion](https://ochen1.github.io/google-meet-discord-alerter/ticket.html) or email o.chen1@share.epsb.ca to help develop!",
                        "inline": False
                    }
                ]
            }]
        }
    )


def check():
    hours = (time() / 3600) % 24
    if skip[0] < hours < skip[1]:
        return
    global out
    for i, code in enumerate(codes):
        print('Testing:', code, sep='\t')
        rf = popen(' '.join(["python3", scriptdir + "test2.py", code[1]]))
        rc = rf.read()
        print(rc)
        ret = rf.close()
        ret = 0 if not ret else WEXITSTATUS(ret)

        if getenv("TEST2_DEBUG_LOG_ENDPOINT") is not None:
            post(
                getenv("TEST2_DEBUG_LOG_ENDPOINT"),
                json={
                    "content": "`{}`\n```\n{}\n```".format(
                        ' - '.join([str(i), "{0} ({2}) - {1}".format(*code), str(ret)]), rc)
                }
            )

        serialized = dict(map(lambda line: tuple(line.split(':\t', 1)), rc.strip().split('\n')))
        serialized['retcode'] = ret
        serialized['classname'] = code[0]
        serialized['classcode'] = code[2]
        serialized['input'] = code[1]
        print(repr(serialized))
        if ret == 0 and ret != out[i][0] and serialized.get('organization') is not None:
            runwarning(serialized)
        if ret != 0 and out[i][0] == 0 and ret != out[i][0]:
            post(
                getenv('WEBHOOK'),
                json={
                    'content': "It looks like the **<:gmeet:836629017774915625> Google Meet** just ended! :tada:"
                }
            )
        out[i] = [6 if ret == 0 and serialized.get('organization') is None else ret, time()]


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


@app.route('/index')
def locateIndex():
    return Response('\n'.join([
        '/index',
        '/',
        '/globals',
        '/force',
    ]), content_type="text/plain")


@app.route('/')
@auth.login_required
def index():
    s = f"""{sys.version}
Program is running.
Current Time: {time()}
Current Time: {strftime('%Y-%m-%d %H:%M:%S %Z', gmtime())}
Up since: {strftime('%Y-%m-%d %H:%M:%S %Z', gmtime(up))} ({up})
Uptime: {str(timedelta(seconds=round(time() - up, 2)))}
Codes: {repr(codes)}
Output: {', '.join(map(repr, out))}
"""
    return Response(s, content_type="text/plain")


@app.route('/globals')
@auth.login_required
def globalsIndex():
    s = f"Globals:\n{pformat(dict(filter(lambda li: li[0] != 'users' and li[0] != 'admins', globals().items())))}\n\
Note: global variables \"users\" and \"admins\" have been excluded from the list for security reasons.\
"
    return Response(s, content_type="text/plain")


@app.route('/force')
@auth.login_required
def forceCheck():
    if auth.current_user() in admins:
        check()
        return "OK!"
    else:
        return "Denied."


@app.route('/ping')
def ping():
    return "Pong!"


if __name__ == "__main__":
    print("Start.")
    webThread = Thread(target=app.run, kwargs={
        'host': "0.0.0.0",
        'port': getenv('PORT')
    })
    webThread.daemon = True
    webThread.start()
    try:
        while True:
            sleep(60 - (time() % 60))
            check()
    except KeyboardInterrupt:
        print()
    finally:
        print("Stop.")
        sys.exit()
