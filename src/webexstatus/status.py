#!/usr/bin/env python3

########################################################################################################################
# status.py      Relay call status from Webex Desk Pro to MQTT
# Author:               Steve Luzynski - sluzynsk@cisco.com
# Date:                 Jan 29, 2021
########################################################################################################################

import requests
import urllib3
import os
from paho.mqtt import publish
from flask import Flask
from flask import request
from flask_api import status
from flask_restful import Api

app = Flask(__name__)
app.config.from_object(app)
api = Api(app)

""" Set script variables from environment"""
""" mqtt port is optional and defaults to 1883, only need to define if it's different"""

# Webex DeskPro Config
if os.environ.get("SERVER_IP"):
    app.config.update(dict(SERVER_IP=os.environ.get("SERVER_IP")))

if os.environ.get("DESKPRO_TOKEN"):
    app.config.update(dict(DESKPRO_TOKEN=os.environ.get("DESKPRO_TOKEN")))

if os.environ.get("DESKPRO_IP"):
    app.config.update(dict(DESKPRO_IP=os.environ.get("DESKPRO_IP")))

if os.environ.get("MQTT_HOST"):
    app.config.update(dict(MQTT_HOST=os.environ.get("MQTT_HOST")))

if os.environ.get("MQTT_PORT"):
    app.config.update(dict(MQTT_PORT=os.environ.get("MQTT_PORT")))
else:
    app.config.update(dict(MQTT_PORT="1883"))

if os.environ.get("MQTT_USERNAME"):
    app.config.update(dict(MQTT_USERNAME=os.environ.get("MQTT_USERNAME")))

if os.environ.get("MQTT_PASSWORD"):
    app.config.update(dict(MQTT_PASSWORD=os.environ.get("MQTT_PASSWORD")))

# Broker Configuration

auth = {
    "username": app.config['MQTT_USERNAME'],
    "password": app.config['MQTT_PASSWORD'],
}


def setup():
    """
        Runs on initial script setup to attach to the Desk Pro API
        and subscribe to the events we want

    :return:
    """
    urllib3.disable_warnings()

    url = f"https://{app.config['DESKPRO_IP']}/putxml"
    payload = (
        "<Command>"
        "    <HttpFeedback>"
        '        <Register command="true">'
        "            <FeedbackSlot>1</FeedbackSlot>"
        "            <ServerUrl>http://" + app.config['SERVER_IP'] + ":5001</ServerUrl>"
        "            <Format>JSON</Format>"
        '            <Expression item="1">/Event/CallSuccessful</Expression>'
        '            <Expression item="2">/Event/CallDisconnect</Expression>'
        "        </Register>"
        "    </HttpFeedback>"
        "</Command>"
    )

    headers = {"Authorization": f"Basic {app.config['DESKPRO_TOKEN']}"}

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False
    )

    mqtt_publish("webexDP/Available", "True")

    mqtt_publish("webexDP/InACall", "False")


def mqtt_publish(mqtt_msg, payload):
    # Publish message to a local MQTT broker for other clients to subscribe

    print(f"Topic: {mqtt_msg} Host: {app.config['MQTT_HOST']} Port: {app.config['MQTT_PORT']}")

    publish.single(
        topic=mqtt_msg,
        hostname=app.config['MQTT_HOST'],
        payload=payload,
        port=int(app.config['MQTT_PORT']),
        keepalive=60,
        auth=auth,
    )


@app.errorhandler(Exception)
def on_exit(error):
    url = f"https://{app.config['DESKPRO_IP']}/putxml"
    payload = (
        "<Command>"
        "    <HttpFeedback>"
        '        <Deregister command="true">'
        "            <FeedbackSlot>1</FeedbackSlot>"
        "        </Deregister>"
        "    </HttpFeedback>"
        "</Command>"
    )
    headers = {"Authorization": f"Basic {app.config['DESKPRO_TOKEN']}"}

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False
    )

    print(f"Deregistering to try to clean up. Error code I got was {error}.")
    print(response.text)

    # Try to take the HA entity offline on my way down
    mqtt_publish("webexDP/Available", "False")

    return "ok"


@app.post("/")
def index_post():
    incoming = request.json

    event = next(iter(incoming['Event']))

    if event == 'CallDisconnect':
        print("Disconnected")
        mqtt_publish("webexDP/InACall", "False")
    elif event == 'CallSuccessful':
        print("Connected to new call")
        mqtt_publish("webexDP/InACall", "True")
    else:
        print("Unknown event I didn't subscribe to. Wierd.")

    return "ok"


@app.post("/onvif/")
def onvif_post():
    print("Someone thinks I'm a camera.")
    return status.HTTP_400_BAD_REQUEST


@app.get("/")
def index_get():
    print("GET call.")
    return status.HTTP_400_BAD_REQUEST


if __name__ == "__main__":
    setup()
    app.run(host="0.0.0.0", port=5001)
    on_exit(0)
