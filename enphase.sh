#!/bin/sh
echo Polling enphase envoy...

. `dirname $0`/env.sh

python ./pullAndSend.py --url $ENVOY_URL --per_inverter_url $ENVOY_PER_INVERTER_URL --per_inverter_username $ENVOY_USERNAME --per_inverter_password $ENVOY_PASSWORD