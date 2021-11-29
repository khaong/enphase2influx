#!/bin/sh
. ./env.sh

while [ 1 ]; do
    python2 ./pullAndSend.py --url $ENVOY_URL --per_inverter_url $ENVOY_PER_INVERTER_URL --per_inverter_username $ENVOY_USERNAME --per_inverter_password $ENVOY_PASSWORD
    sleep 15
done
