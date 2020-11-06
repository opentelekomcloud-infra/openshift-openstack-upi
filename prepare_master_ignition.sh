#!/usr/bin/env bash

for index in $(seq 0 2); do
    MASTER_HOSTNAME="$INFRA_ID-master-$index\n"
    python3 -c "import base64, json, sys;
ignition = json.load(sys.stdin);
files = [];
if 'storage' in ignition:
    files = ignition['storage'].get('files', []);
files.append({'path': '/etc/hostname', 'mode': 420, 'contents': {'source': 'data:text/plain;charset=utf-8;base64,' + base64.standard_b64encode(b'$MASTER_HOSTNAME').decode().strip(), 'verification': {}}, 'filesystem': 'root'});
if not 'storage' in ignition:
    ignition['storage'] = dict();
ignition['storage']['files'] = files;
json.dump(ignition, sys.stdout)" <master.ign >"$INFRA_ID-master-$index-ignition.json"
done
