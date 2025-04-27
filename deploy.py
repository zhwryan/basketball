# -*- coding: utf-8 -*-

import json
import os
import threading

SETTING = None
print_lock = threading.Lock()


def log(*args):
    with print_lock:
        print(*args)


config_json = "config.json"
assert os.path.isfile(config_json), "without config.json"
with open(config_json, 'r') as f:
    SETTING = json.load(f)
    for key, val in SETTING["OS_ENVS"].items():
        os.environ[key] = val
