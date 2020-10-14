#! /usr/bin/python3

import json
import requests

class hdns():
    def __init__(self, token):
        self.baseUrl = "https://dns.hetzner.com/api/v1"
        self.token = token

    def getAllZones(self):
        __name__ = "getAllZones"
        try:
            response = requests.get(
                url="{baseUrl}/zones".format(baseUrl=self.baseUrl),
                headers={
                    "Auth-API-Token": self.token,
                },
            )
            print('[{name}] Response HTTP Status Code: {status_code}'.format(
                name=__name__, status_code=response.status_code))
            return json.loads(response.content)["zones"]
        except requests.exceptions.RequestException:
            print('HTTP Request failed')

    def getAllRecords(self, zoneId, record_type="All"):
        __name__ = "getAllRecords"
        try:
            response = requests.get(
                url="{baseUrl}/records".format(baseUrl=self.baseUrl),
                params={
                    "zone_id": zoneId,
                },
                headers={
                    "Auth-API-Token": self.token,
                },
            )
            print('[{name}] Response HTTP Status Code: {status_code}'.format(
                name=__name__, status_code=response.status_code))
            records = json.loads(response.content)["records"]
            if record_type:
                return [record for record in records if record["type"] == record_type]
            elif record_type == "All":
                return records
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
    
    def updateRecord(self, recordId, zoneId, name, value, record_type="A", ttl=86400):
        __name__ = "updateRecord"
        try:
            response = requests.put(
                url="{baseUrl}/records/{recordId}".format(baseUrl=self.baseUrl, recordId=recordId),
                headers={
                    "Content-Type": "application/json",
                    "Auth-API-Token": self.token,
                },
                data=json.dumps({
                    "value": value,
                    "ttl": ttl,
                    "type": record_type,
                    "name": name,
                    "zone_id": zoneId
                })
            )
            print('[{name}] Response HTTP Status Code: {status_code}'.format(
                name=__name__, status_code=response.status_code))
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
    
    def createRecord(self, zoneId, name, value, record_type="A", ttl=86400):
        __name__ = "createRecord"
        try:
            response = requests.post(
                url="{baseUrl}/records".format(baseUrl=self.baseUrl),
                headers={
                    "Content-Type": "application/json",
                    "Auth-API-Token": self.token,
                },
                data=json.dumps({
                    "value": value,
                    "ttl": ttl,
                    "type": record_type,
                    "name": name,
                    "zone_id": zoneId
                })
            )
            print('[{name}] Response HTTP Status Code: {status_code}'.format(
                name=__name__, status_code=response.status_code))
        except requests.exceptions.RequestException:
            print('HTTP Request failed')

if __name__ == "__main__":
    exit()
