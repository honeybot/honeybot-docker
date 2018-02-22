#!/usr/bin/env python
import os
import ssl
import sys
import json
import redis
import asyncio
import websockets
from subprocess import call
from datetime import datetime

LOG_FILE = "/var/log/bot_update.log"

if not os.environ["HB_ID"]:
    log("{} [ERROR] HB_GROUPID environment variable is not set".format(
        str(datetime.now())))
    sys.exit("HB_GROUPID environment variable is not set")

if not os.environ["HB_ID"]:
    log("{} [ERROR] HB_GROUPID environment variable is not set".format(
        str(datetime.now())))
    sys.exit("HB_GROUPID environment variable is not set")

if not os.environ["HG_HOST"]:
    log("{} [ERROR] HG_HOST environment variable is not set".format(
        str(datetime.now())))
    sys.exit("HG_HOST environment variable is not set")

if not os.environ["HG_KEY"]:
    log("{} [ERROR] HG_KEY environment variable is not set".format(
        str(datetime.now())))
    sys.exit("HG_KEY environment variable is not set")


def log(data):
    with open(LOG_FILE, "a") as f:
        f.write("{}\n".format(data))


async def send_data(data):
    link = "wss://{}:443/policies/{}".format(
        os.environ["HG_HOST"], os.environ["HB_GROUPID"])
    context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
    async with websockets.connect(link, ssl=context) as websocket:
        await websocket.send(data)
        response = await websocket.recv()
        policies = json.loads(response)
        count = {"changed": 0, "new": 0}
        for item in policies:
            for plugin in item["policy"]["plugins"]:
                call(["luarocks","install","wtf-plugin-{}".format(plugin.replace(".","-"))])
            for storage in item["policy"]["storages"]:
                call(["luarocks","install","wtf-storage-{}".format(storage.replace(".","-"))])
            for action in item["policy"]["actions"]:
                call(["luarocks","install","wtf-action-{}".format(action.replace(".","-"))])

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
                    call(["service", "openresty", "reload"])
            else:
                count["new"] += 1
                with open(policy_json, "w") as f:
                    f.write(json.dumps(item["policy"]))
                call(["service", "openresty", "reload"])
        if count["changed"] > 0 or count["new"] > 0:
            log("{} [INFO] Added {} policies, changed {}".format(
                str(datetime.now()), count["new"], count["changed"]))
try:
    data = {
        "id": os.environ["HB_ID"],
        "key": os.environ["HG_KEY"]
    }
    asyncio.get_event_loop().run_until_complete(send_data(json.dumps(data)))
except Exception as e:
    log("{} [ERROR] {}".format(str(datetime.now()), e))
