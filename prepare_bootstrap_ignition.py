#!/usr/bin/env python3

import base64
import json
import os

with open('bootstrap.ign', 'r') as f:
    ignition = json.load(f)

storage = ignition.get('storage', {})
files = storage.get('files', [])

infra_id = os.environ.get('INFRA_ID', 'openshift').encode()
hostname_b64 = base64.standard_b64encode(infra_id + b'-bootstrap\n').decode().strip()
files.append(
{
    'path': '/etc/hostname',
    'mode': 420,
    'contents': {
        'source': 'data:text/plain;charset=utf-8;base64,' + hostname_b64,
        'verification': {}
    },
})


storage['files'] = files
ignition['storage'] = storage

with open('bootstrap.ign', 'w') as f:
    json.dump(ignition, f)
