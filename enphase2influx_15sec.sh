#!/usr/bin/env bash
source ./venv/bin/activate
. ./env.sh

while [ 1 ]; do
    python3 ./pullAndSend.py --url $ENVOY_URL --per_inverter_url $ENVOY_PER_INVERTER_URL --auth_token_file $AUTH_TOKEN_FILE
    sleep 15
done
