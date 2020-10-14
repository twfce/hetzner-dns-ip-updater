#! /usr/bin/python3

import os
import json
from time import sleep
from datetime import datetime
from colored import fg, attr
import paho.mqtt.client as mqtt

def onMQTTConnect(client, userdata, flags, rc):
    if rc == 0:
        print ("{color}[+] Connected to MQTT broker (Return code: {rc}){reset}".format(color=fg(2), rc=rc, reset=attr(0)))
        client.publish("/mqtt2influxdb", "Hello World!")
    else:
        print ("{color}[-] Not connected to MQTT broker (Return code: {rc}){reset}".format(color=fg(1), rc=rc, reset=attr(0)))


def onMQTTPublish(client, userdata, mid):
    print ("{color}[*] Published to MQTT broker (Message ID: {mid}){reset}".format(color=fg(135), mid=mid, reset=attr(0)))

def onMQTTMessage(client, userdata, msg):
    print ("{color}[*] Received message on topic {topic}{reset}".format(color=fg(135), topic=msg.topic , reset=attr(0)))
    print (msg.payload)

def main():
    mqttBroker = os.environ["MQTT_BROKER"]
    mqttUsername = os.environ["MQTT_USERNAME"]
    mqttPassword = os.environ["MQTT_PASSWORD"]
    if "MQTT_PORT" in os.environ:
        mqttPort = os.environ["MQTT_PORT"]
    else:
        mqttPort = 1883

    client = mqtt.Client()
    client.on_connect = onMQTTConnect
    client.on_publish = onMQTTPublish
    client.on_message = onMQTTMessage
    client.username_pw_set(username=mqttUsername, password=mqttPassword)
    client.connect(mqttBroker, mqttPort, 60)
    client.subscribe("home/#")
    client.loop_forever()

if __name__ == "__main__":
    main()
