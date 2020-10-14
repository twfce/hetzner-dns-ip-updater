#! /usr/bin/python3

import os
import json
from time import sleep
from datetime import datetime
from colored import fg, attr
import paho.mqtt.client as mqtt
from hdns import hdns

def updateDNSRecords(ip):
    api = hdns(hdnsToken)
    print ("{color}[*] Requesting all zones{reset}".format(color=fg(3), reset=attr(0)))
    zones = [zone for zone in api.getAllZones() if zone["name"] in config["zones"]] 

    for zone in zones:
        print ("{color}[{zone}] Requesting all registered A records for zone{reset}".format(color=fg(3), zone=zone["name"], reset=attr(0)))
        registered_records = api.getAllRecords(zone["id"], record_type="A")        
        print ("{color}[{zone}] Checking configured records{reset}".format(color=fg(3), zone=zone["name"], reset=attr(0)))
        for record in config["zones"][zone["name"]]["records"]:
            registered_record = next((rr for rr in registered_records if rr["name"] == record), None)
            if registered_record:
                print ("{color}[{record}.{zone}] Already registered. Going to update record{reset}".format(color=fg(3), record=record, zone=zone["name"], reset=attr(0)))
                api.updateRecord(recordId=registered_record["id"], zoneId=zone["id"], name=registered_record["name"], value=ip)
                print ("{color}[{record}.{zone}] Updated{reset}".format(color=fg(2), record=record, zone=zone["name"], reset=attr(0)))
            else:
                print ("{color}[{record}.{zone}] Not registered. Going to create new record{reset}".format(color=fg(3), record=record, zone=zone["name"], reset=attr(0)))

                api.createRecord(zoneId=zone["id"], name=record, value=ip)
                print ("{color}[{record}.{zone}] Created{reset}".format(color=fg(2), record=record, zone=zone["name"], reset=attr(0)))

def checkIpChanged(report):
    report = json.loads(report)
    newIP = report['external_ip']
    if os.path.isfile(".remember"):
        f = open(".remember", "r")
        lastIP = f.read()
        f.close()
        newIP = report['external_ip']

        if lastIP == newIP:
            print ("{color}[*] IP did not change. It's still {IP}{reset}".format(color=fg(3), IP=newIP, reset=attr(0)))
        else:
            print ("{color}[*] IP changed! From {lastIP} to {newIP}{reset}".format(color=fg(214), lastIP=lastIP, newIP=newIP, reset=attr(0)))
            f = open(".remember", "w")
            f.write(newIP)
            f.close()
            print ("{color}[+] Updated IP cache{reset}".format(color=fg(2), reset=attr(0)))
            updateDNSRecords(newIP)
    else:
        print ("{color}[*] This is the first run. IP is {IP}{reset}".format(color=fg(3), IP=newIP, reset=attr(0)))
        updateDNSRecords(newIP)
        f = open(".remember", "w")
        f.write(newIP)
        f.close()

def onMQTTConnect(client, userdata, flags, rc):
    if rc == 0:
        print ("{color}[+] Connected to MQTT broker (Return code: {rc}){reset}".format(color=fg(2), rc=rc, reset=attr(0)))
        client.publish("home/public-ip-changer", "Hello World! I'm waiting for reports.")
    else:
        print ("{color}[-] Not connected to MQTT broker (Return code: {rc}){reset}".format(color=fg(1), rc=rc, reset=attr(0)))


def onMQTTPublish(client, userdata, mid):
    print ("{color}[*] Published to MQTT broker (Message ID: {mid}){reset}".format(color=fg(3), mid=mid, reset=attr(0)))

def onMQTTMessage(client, userdata, msg):
    print ("{color}[*] Received message on topic {topic}{reset}".format(color=fg(3), topic=msg.topic , reset=attr(0)))
    print (msg.payload)
    checkIpChanged(msg.payload)

def main():
    client = mqtt.Client()
    client.on_connect = onMQTTConnect
    client.on_publish = onMQTTPublish
    client.on_message = onMQTTMessage
    client.username_pw_set(username=mqttUsername, password=mqttPassword)
    client.connect(mqttBroker, mqttPort, 60)
    client.subscribe(mqttTopic)
    client.loop_forever()

if __name__ == "__main__":
    try:
        hdnsToken = os.environ["HDNS_TOKEN"]
    except KeyError:
        print ("{color}[X] You need to specify env variable HDNS_TOKEN!{reset}".format(color=fg(1), reset=attr(0)))
        exit()
    mqttBroker = os.environ["MQTT_BROKER"]
    mqttUsername = os.environ["MQTT_USERNAME"]
    mqttPassword = os.environ["MQTT_PASSWORD"]
    mqttPort = 1883 if "MQTT_PORT" not in os.environ else os.environ["MQTT_PORT"]
    mqttTopic = "home/fritzBox/report" if "MQTT_TOPIC" not in os.environ else os.environ["MQTT_TOPIC"]
   
    config = json.loads(open("config.json").read())
    main()
