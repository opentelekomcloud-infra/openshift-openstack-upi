#!/usr/bin/env bash

docker run -i --rm quay.io/coreos/fcct:v0.2.0 -pretty -strict < \
haproxy-coreos.fcc > $INFRA_ID-haproxy-ignition.json
