#!/usr/bin/env python

# Copyright (C) 2019 Iwan Timmer
# Copyright (C) 2017 Google Inc.
# SPDX-License-Identifier: Apache-2.0

import sys
import argparse
import json
import os.path
import pathlib
import importlib

import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.file_helpers import existing_file
from google.assistant.library.device_helpers import register_device

from handler import Handler

WARNING_NOT_REGISTERED = """
    This device is not registered. This means you will not be able to use
    Device Actions or see your device in Assistant Settings. In order to
    register this device follow instructions at:

    https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device-model-id', '--device_model_id', type=str, metavar='DEVICE_MODEL_ID', required=False, help='the device model ID registered with Google')
    parser.add_argument('--project-id', '--project_id', type=str, metavar='PROJECT_ID', required=False, help='the project ID used to register this device')
    parser.add_argument('--nickname', type=str, metavar='NICKNAME', required=False, help='the nickname used to register this device')
    parser.add_argument('--device-config', type=str, metavar='DEVICE_CONFIG_FILE', default=os.path.join(os.path.expanduser('~/.config'), 'gassistant', 'device.json'), help='path to store and read device configuration')
    parser.add_argument('--credentials', type=existing_file, metavar='OAUTH2_CREDENTIALS_FILE', default=os.path.join(os.path.expanduser('~/.config'), 'gassistant', 'credentials.json'), help='path to store and read OAuth2 credentials')
    parser.add_argument('--plugins', nargs='+', type=str, metavar='PLUGINS', default=[], help='plugin to be loaded')

    args = parser.parse_args()
    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None, **json.load(f))

    device_model_id = None
    project_id = None
    last_device_id = None
    try:
        with open(args.device_config) as f:
            device_config = json.load(f)
            device_model_id = device_config['model_id']
            project_id = device_config['project_id']
            last_device_id = device_config.get('last_device_id', None)
    except FileNotFoundError:
        pass

    if not args.device_model_id and not device_model_id:
        raise Exception('Missing --device-model-id option')

    # Re-register if "device_model_id" is given by the user and it differs
    # from what we previously registered with.
    should_register = (args.device_model_id and args.device_model_id != device_model_id)

    device_model_id = args.device_model_id or device_model_id
    project_id = args.project_id or project_id

    with Assistant(credentials, device_model_id) as assistant:
        handler = Handler(assistant.start())
        print(args)
        for plugin in args.plugins:
            try:
                handler.add_plugin(importlib.import_module("plugins." + plugin).getInstance())
            except ImportError:
                print("Can not load plugin {plugin}".format(plugin=plugin), file=sys.stderr)

        device_id = assistant.device_id
        print('Device Model ID:', device_model_id)
        print('Device ID:', device_id + '\n')

        # Re-register if "device_id" is different from the last "device_id":
        if should_register or (device_id != last_device_id):
            if args.project_id:
                register_device(args.project_id, credentials, device_model_id, device_id, args.nickname)
                pathlib.Path(os.path.dirname(args.device_config)).mkdir(exist_ok=True)
                with open(args.device_config, 'w') as f:
                    json.dump({
                        'last_device_id': device_id,
                        'model_id': device_model_id,
                        'project_id': project_id,
                    }, f)
            else:
                print(WARNING_NOT_REGISTERED)

        handler.start()

if __name__ == '__main__':
    main()
