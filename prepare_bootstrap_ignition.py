#!/usr/bin/env python3

import base64
import json
import sys

from pathlib import Path

import openstack

infra_id = sys.argv[1]
file_loc = sys.argv[2] or ''
bootstrap_file = Path(file_loc, 'bootstrap.ign').resolve()

with open(bootstrap_file, 'r') as f:
    ignition = json.load(f)

storage = ignition.get('storage', {})
files = storage.get('files', [])

hostname_b64 = base64.standard_b64encode(
    infra_id.encode() + b'-bootstrap\n').decode().strip()

hostnamefile_found = False
for f in files:
    if f['path'] == '/etc/hostname':
        hostnamefile_found = True

if not hostnamefile_found:
    files.append(
        {
            'path': '/etc/hostname',
            'mode': 420,
            'contents': {
                'source':
                    'data:text/plain;charset=utf-8;base64,' + hostname_b64,
                'verification': {}
            },
        })

    storage['files'] = files
    ignition['storage'] = storage

    with open(bootstrap_file, 'w') as f:
        json.dump(ignition, f)

conn = openstack.connect()

container = conn.create_container(infra_id)
conn.set_container_access(infra_id, "public")
conn.delete_object(infra_id, 'bootstrap.ign')
conn.object_store.create_object(infra_id, 'bootstrap.ign',
                                data=json.dumps(ignition))

with open("bootstrap-ignition.json", "r") as f:
    ignition = json.load(f)

ignition["ignition"]["config"]["merge"][0]["source"] = (
    "https://swift.eu-de.otc.t-systems.com/v1/AUTH_{pref}/"
    "{infra_id}/bootstrap.ign".format(
        pref=conn.current_project_id,
        infra_id=infra_id)
)

bootstrap_ignition_file = Path(
    file_loc,
    "{infra_id}-bootstrap-ignition.json".format(infra_id=infra_id)
).resolve()


with open(bootstrap_ignition_file, "w") as f:
    json.dump(ignition, f)

master_ignition_file = Path(file_loc, 'master.ign').resolve()

with open(master_ignition_file, 'r') as f:
    master_ignition = json.load(f)
for i in range(0, 3):
    ignition = master_ignition.copy()
    hostname = '%s-master-%s' % (infra_id, i)
    files = []
    if 'storage' in ignition:
        files = ignition['storage'].get('files', [])
    files.append(
        {
            'path': '/etc/hostname',
            'mode': 420,
            'contents': {
                'source': 'data:text/plain;charset=utf-8;base64,' +
                base64.standard_b64encode(hostname.encode()).decode().strip(),
                'verification': {}
            },
            'filesystem': 'root'
        })
    if 'storage' not in ignition:
        ignition['storage'] = dict()
    ignition['storage']['files'] = files
    with open(
        Path(file_loc, '%s-ignition.json' % hostname).as_posix(), 'w'
    ) as f:
        json.dump(ignition, f)
