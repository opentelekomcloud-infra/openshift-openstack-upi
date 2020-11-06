#!/usr/bin/env bash

openstack container create $INFRA_ID
python3 -c '
import openstack
import os
conn=openstack.connect()
conn.set_container_access(os.getenv("INFRA_ID"), "public")'
openstack object delete $INFRA_ID bootstrap.ign

openstack object create $INFRA_ID bootstrap.ign

swift_prefix=`openstack container show $INFRA_ID -f value -c account`
export swift_prefix

python3 -c '
import base64, json, sys, os

infra_id=os.getenv("INFRA_ID")

with open("bootstrap-ignition.json", "r") as f:
    ignition = json.load(f)

ignition["ignition"]["config"]["merge"][0]["source"] = "https://swift.eu-de.otc.t-systems.com/v1/{pref}/{infra_id}/bootstrap.ign".format(
    pref=os.getenv("swift_prefix"),
    infra_id=infra_id
)
with open("{infra_id}-bootstrap-ignition.json".format(infra_id=infra_id), "w") as f:
    json.dump(ignition, f)

'
