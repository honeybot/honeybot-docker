#!/usr/bin/env python
import os
import ssl
import sys
import json
import redis
import asyncio
import websockets
import subprocess
from datetime import datetime

LOG_FILE = "/var/log/bot_update.log"

def log(data):
    with open(LOG_FILE, "a") as f:
        f.write("{}\n".format(data))

def install_luarocks(_type,data):
    count = 0
    process = subprocess.Popen(
        ["luarocks list"],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    installed = process.stdout.read().splitlines()
    for item in data:
        if item not in installed:
            count += 1
            subprocess.call(["luarocks","install","wtf-{}-{}".format(_type, item.replace(".","-"))])
    return count

async def send_data(data):
    link = "wss://{}:443/policies/{}".format(
        os.environ["HG_HOST"], os.environ["HB_GROUPID"])
    context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
    async with websockets.connect(link, ssl=context) as websocket:
        await websocket.send(data)
        response = await websocket.recv()
        policies = json.loads(response)
        count = {"changed": 0, "new": 0, "plugins": 0, "actions": 0, "storages": 0}
        for item in policies:
            policy_json = "/etc/openresty/wtf-demo-policy/policy/{}.json".format(
                item["policy"]["name"])
            if os.path.exists(policy_json):
                current = open(policy_json, "r").read()
                current = json.loads(current)
                if float(
                        current["version"]) < float(
                        item["policy"]["version"]):
                    count["changed"] += 1
                    with open(policy_json, "w") as f:
                        f.write(json.dumps(item["policy"]))
                    count["plugins"] += install_luarocks("plugin", item["policy"]["plugins"])
                    count["actions"] += install_luarocks("action", item["policy"]["actions"])
                    count["storages"] += install_luarocks("storage", item["policy"]["storages"])
                    subprocess.call(["service", "openresty", "reload"])
            else:
                count["new"] += 1
                with open(policy_json, "w") as f:
                    f.write(json.dumps(item["policy"]))
                count["plugins"] += install_luarocks("plugin", item["policy"]["plugins"])
                count["actions"] += install_luarocks("action", item["policy"]["actions"])
                count["storages"] += install_luarocks("storage", item["policy"]["storages"])
                subprocess.call(["service", "openresty", "reload"])
        if count["changed"] > 0 or count["new"] > 0:
            log("{} [INFO] Added {} policies, changed {}".format(
                str(datetime.now()), count["new"], count["changed"]))
        for item in ["actions", "plugins", "storages"]:
            if count[item] > 0:
                log("{} [INFO] {} {} installed".format(
                    str(datetime.now()), count[item], item))

if "HB_ID" not in  os.environ.keys() or not os.environ["HB_ID"]:
    log("{} [ERROR] HB_ID environment variable is not set".format(
        str(datetime.now())))
    sys.exit("HB_ID environment variable is not set")

if  "HB_GROUPID" not in  os.environ.keys() or not os.environ["HB_GROUPID"]:
    log("{} [ERROR] HB_GROUPID environment variable is not set".format(
        str(datetime.now())))
    sys.exit("HB_GROUPID environment variable is not set")

if  "HB_HOST" not in  os.environ.keys() or not os.environ["HG_HOST"]:
    log("{} [ERROR] HG_HOST environment variable is not set".format(
        str(datetime.now())))
    sys.exit("HG_HOST environment variable is not set")

if  "HG_KEY" not in  os.environ.keys() or not os.environ["HG_KEY"]:
    log("{} [ERROR] HG_KEY environment variable is not set".format(
        str(datetime.now())))
    sys.exit("HG_KEY environment variable is not set")

try:
    data = {
        "id": os.environ["HB_ID"],
        "key": os.environ["HG_KEY"]
    }
    asyncio.get_event_loop().run_until_complete(send_data(json.dumps(data)))
except Exception as e:
    log("{} [ERROR] {}".format(str(datetime.now()), e))
