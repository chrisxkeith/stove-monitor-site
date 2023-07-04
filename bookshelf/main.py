# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import firestore
from flask import current_app, flash, Flask, Markup, redirect, render_template
from flask import request, url_for
from google.cloud import error_reporting
import google.cloud.logging
import storage

from pyparticleio.ParticleCloud import ParticleCloud
from dotenv import load_dotenv
import os
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)
app.config.update(
    SECRET_KEY='secret',
    MAX_CONTENT_LENGTH=8 * 1024 * 1024,
    ALLOWED_EXTENSIONS=set(['png', 'jpg', 'jpeg', 'gif'])
)

app.debug = False
app.testing = False

# Configure logging
if not app.testing:
    logging.basicConfig(level=logging.INFO)
    client = google.cloud.logging.Client()
    # Attaches a Google Stackdriver logging handler to the root logger
    client.setup_logging()

class Sensor:
    latest_event = None

    def __init__(self, particleCloud, deviceName, eventName):
        device = [d for d in particleCloud.devices_list if d.name == deviceName][0]
        device.subscribe(eventName, self.handle_call_back)
        try:
            device.getData("")
        except Exception as e:
            print(repr(e) + ", deviceName: " + deviceName + ", eventName: " + eventName)

    def handle_call_back(self, event_data):
        self.latest_event = event_data

class TemperatureSensor(Sensor):
    latest_temperature_event = None

    def handle_call_back(self, event_data):
        super().handle_call_back(event_data)
        if self.latest_event["event_name"] == "Temperature":
            self.latest_temperature_event = event_data

    def getDisplayVals(self):
        temperature = "No data yet"
        if (self.latest_temperature_event):
            temperature = str(self.latest_event["data"])
        return temperature

class LightSensor(Sensor):
    latest_on_event = None

    def handle_call_back(self, event_data):
        super().handle_call_back(event_data)
        if self.latest_on_event is None and event_data["data"] == "true":
            self.latest_on_event = self.latest_event
        if event_data["data"] == "false":
            self.latest_on_event = None

    def getDisplayVals(self):
        status = "Off"
        on_time = ""
        elapsed_time = ""
        if (self.latest_event):
            if self.latest_event["data"] == 'true':
                status = "On"
        else:
            status = "No data yet"
        if self.latest_on_event:
            [ on_time, elapsed_time ] = getTimeVals(datetime.strptime(self.latest_on_event["published_at"], "%Y-%m-%dT%H:%M:%S.%f%z"))
            elapsed_time += " elapsed"
        return [ status, on_time, elapsed_time ]

env_file_err = None
if os.path.exists("./.env"):
    load_dotenv("./.env")
    particleCloud = ParticleCloud(username_or_access_token=os.getenv("ACCESS_TOKEN"))
    lightSensor = LightSensor(particleCloud, "photon-07", "Light sensor")
    temperatureSensor = TemperatureSensor(particleCloud, "photon-05", "Temperature")
else:
    env_file_err = "No file: ./.env"

def getTimeString(theDateTime):
    return theDateTime.astimezone(ZoneInfo('US/Pacific')).strftime('%I:%M %p')

def getElapsedTime(pastTime):
    now = datetime.now(ZoneInfo('US/Pacific'))
    elapsedSeconds = now - pastTime
    mins = int(elapsedSeconds.total_seconds() / 60)
    secs = int(elapsedSeconds.total_seconds() % 60)
    return "{:0>2}:{:0>2}".format(mins, secs)

def getTimeVals(ts):
    on_time = getTimeString(ts)
    elapsed_time = getElapsedTime(ts)
    return [ on_time, elapsed_time]

@app.route('/')
def list():
    on_time = ""
    elapsed_time = ""
    temperature = ""
    if env_file_err:
        status = env_file_err
    else:
        [ status, on_time, elapsed_time ] = lightSensor.getDisplayVals()
        temperature = temperatureSensor.getDisplayVals()
    return render_template('main.html', latest_event = status, on_time = on_time, elapsed_time = elapsed_time,
        temperature = temperature)

@app.route('/status')
def view():
    return render_template('status.html', latest_event = lightSensor.latest_event,
        latest_on_event = lightSensor.latest_on_event,
        latest_temperature_event = temperatureSensor.latest_temperature_event)

@app.route('/logs')
def logs():
    logging.info('Hey, you triggered a custom log entry. Good job!')
    flash(Markup('''You triggered a custom log entry. You can view it in the
        <a href="https://console.cloud.google.com/logs">Cloud Console</a>'''))
    return redirect(url_for('.list'))


@app.route('/errors')
def errors():
    raise Exception('This is an intentional exception.')


# Add an error handler that reports exceptions to Stackdriver Error
# Reporting. Note that this error handler is only used when debug
# is False
@app.errorhandler(500)
def server_error(e):
    client = error_reporting.Client()
    client.report_exception(
        http_context=error_reporting.build_flask_context(request))
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


# This is only used when running locally. When running live, gunicorn runs
# the application.
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
