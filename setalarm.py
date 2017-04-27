#!/usr/bin/env python

import urllib
import json
import os
import httplib2
import datetime

from __future__ import print_function
from flask import Flask
from flask import request
from flask import make_response

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") != "alarm.set":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    eventdate = parameters.get("date")
    eventtime = parameters.get("time")
    
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
      
    event = {
       'summary': 'My Alarm',
       'location': 'home sweet home',
       'description': 'webhook event',
       'start':{'dateTime': '2017-04-29T17:00:00-07:00','timeZone': 'America/Los_Angeles',},
       'end':{'dateTime': '2017-04-29T17:00:00-07:00','timeZone': 'America/Los_Angeles',},
       'recurrence': ['RRULE:FREQ=DAILY;COUNT=2'],
       'attendees': [{'email': 'lpage@example.com'},{'email': 'sbrin@example.com'},],
       'reminders': {
       'useDefault': False,
       'overrides': [
       {'method': 'email', 'minutes': 24 * 60},
       {'method': 'popup', 'minutes': 10},
       ],
       },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    speech = "Welcome to Ritz webhook " + "Event Created"
    print('Event created:')
    print("Response:")
    print(speech)
    return {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "agent"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')

