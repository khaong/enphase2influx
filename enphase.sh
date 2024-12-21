#!/bin/sh
source ./venv/bin/activate
. ./env.sh

echo Polling enphase envoy...
python3 ./pullAndSend.py --url $ENVOY_URL --per_inverter_url $ENVOY_PER_INVERTER_URL --auth_token_file=$AUTH_TOKEN_FILE