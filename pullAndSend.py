#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""PollAndPushServer.py: Script for query production values from Enphase-S gateway hosted
on a local server server and push data on InfluxDb.."""

__author__ = "César Papilloud, Pierre-A. Mudry"
__copyright__ = "Copyright 2018, FireMON, WaterMON, EarthMON, SpaceMON"
__version__ = "1.1.0"

import json
import requests
from requests.auth import HTTPDigestAuth
from influxdb import InfluxDBClient
import time
import progressbar
import argparse

# Sleep time setting
__sleepTime__ = 30
# InfluxDB settings
__host__ = 'localhost'
__port__ = 8086
__user__ = 'admin'
__password__ = 'admin'
__dbname__ = 'enphase'

# Getting arguments
parser = argparse.ArgumentParser()
parser.add_argument('--url', default="http://enphase.ayent/production.json",
        help='the URL of production.json (default: http://enphase.ayent/production.json)')
parser.add_argument('--per_inverter_url', default="http://envoy.local/api/v1/production/inverters",
        help='the URL of the per-inverter api (default: http://envoy.local/api/v1/production/inverters)')
parser.add_argument('--per_inverter_username',
        help='the username for the per-inverter api')
parser.add_argument('--per_inverter_password',
        help='the password for the per-inverter api')

args = parser.parse_args()
__url__ = args.url
__per_inverter_url__ = args.per_inverter_url
__per_inverter_username__ = args.per_inverter_username
__per_inverter_password__ = args.per_inverter_password

# Last reading time, used to avoid pushing same values twice
lastProductionInverterTime = 0
lastProductionEimTime = 0
lastConsumptionTime = 0
lastNetConsumptionTime = 0

"""Functions definitions"""
def pushData(data, seriesName, client):
        """Push data  into InfluxDB"""
        points = [{
                "measurement": seriesName,
                "time": data['readingTime'],
                "fields": data
        }]
        client.write_points(points, time_precision='s')

def transform_inverter_status(status):
        """Transform an inverter status into an influx record"""
        array_id = None

        nw_row_1 = [
            "121834016762",
            "121834017142",
            "121834017531",
            "121834016909",
            "121834017063",
            "121834016079",
            "121834015898",
        ]
        nw_row_2 = [
            "121834017129",
            "121834017050",
            "121834017135",
            "121834016760",
            "121834016763",
            "121834017765",
            "121834017118"
        ]
        sw_row = [
            "121834012995",
            "121834017144",
            "121834017073",
            "121834012414"
        ]

        if status['serialNumber'] in nw_row_1:
            array_id = 'NW_1'
        if status['serialNumber'] in nw_row_2:
            array_id = 'NW_2'
        if status['serialNumber'] in sw_row:
            array_id = 'SW'

        return {
                "measurement": "per_inverter",
                "tags": {
                    "serialNumber": status['serialNumber'],
                    "array": array_id
                },
                "time": status['lastReportDate'],
                "fields": {
                    "lastReportWatts": status['lastReportWatts']
                }
        }

client = InfluxDBClient(__host__, __port__, database=__dbname__)

"""Part 1 : Query production data from an url"""
print "************************"
print "Getting Enphase JSON information from server " + __url__
# Query the url
try:
        data = requests.get(__url__, timeout=5).json()

        productionInverterData = data['production'][0]
        productionEimData = data['production'][1]
        consumptionData = data['consumption'][0]
        netconsumptionData = data['consumption'][1]

        """Part 2 : Check if readingTime is different"""
        print "************************"
        print "Time data from general information : ", productionInverterData['readingTime']
        print "Time data from general data EIM : ", productionEimData['readingTime']
        print "Time data from consumption : ", consumptionData['readingTime']
        print "Time data from net consumption : ", netconsumptionData['readingTime']
        print "************************"

        """Part 3 : Push data into InfluxDB, only if time is different"""
        if productionInverterData['readingTime'] > lastProductionInverterTime:
                print "Pushing production data"
                pushData(productionInverterData, "general_info", client)
                lastProductionInverterTime = productionInverterData['readingTime']

        if productionEimData['readingTime'] > lastProductionEimTime:
                print "Pushing general info"
                pushData(productionEimData, "production", client)
                lastProductionEimTime = productionEimData['readingTime']

        if consumptionData['readingTime'] > lastConsumptionTime:
                print "Pushing total consumption data"
                pushData(consumptionData, "total_consumption", client)
                lastConsumptionTime = consumptionData['readingTime']

        if netconsumptionData['readingTime'] > lastNetConsumptionTime:
                print "Pushing net consumption"
                pushData(netconsumptionData, "net_consumption", client)
                lastNetConsumptionTime = netconsumptionData['readingTime']

except Exception as e:
        print e

print "************************"

if __per_inverter_url__ is not None:
        print "Getting Enphase JSON information from server " + __per_inverter_url__
        print "************************"
        try:
                response = requests.get(__per_inverter_url__, auth=HTTPDigestAuth(__per_inverter_username__, __per_inverter_password__), timeout=5)
                if response.status_code is not 200:
                        raise Exception("Could not get a valid response, please check your Per-inverter URL, username and password")
                data = list(map(transform_inverter_status, response.json()))

                print "Pushing production data for %s inverters" % len(data)
                client.write_points(data, time_precision='s')
        except Exception as e:
                print e

        print "************************"
