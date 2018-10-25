#!/usr/bin/env python
import os
import ssl
import sys
import json
import redis
import asyncio
import websockets
from datetime import datetime

LOG_FILE="/var/log/honeybot.log"

if not os.environ["HB_ID"]:
    log("{} [ERROR] HB_ID environment variable is not set".format(str(datetime.now())))
    sys.exit("HB_ID environment variable is not set")

if not os.environ["HG_KEY"]:
    log("{} [ERROR] HG_KEY environment variable is not set".format(str(datetime.now())))
    sys.exit("HG_KEY environment variable is not set")

if not os.environ["HG_HOST"]:
    log("{} [ERROR] HG_HOST environment variable is not set".format(str(datetime.now())))
    sys.exit("HG_HOST environment variable is not set")


def get_from_redis():
    result = []
    r = redis.Redis(unix_socket_path='/var/run/redis/redis.sock')
    for key in r.scan_iter("*"):
        try:
            result.append(json.loads(r.get(key).decode("utf8", "ignore")))
            if "ip" in result and "id" in result and "method" in result:
                r.delete(key)
        except Exception as err:
            print(err)
        if len(result) > 1000:
            break
    return result

def log(data):
    with open(LOG_FILE,"a") as f:
        f.write("{}\n".format(data))

async def send_data(data):
    async with websockets.connect("wss://{}:443".format(os.environ["HG_HOST"]), ssl=ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)) as websocket:
        await websocket.send(json.dumps(data))
        response = await websocket.recv()
        response = json.loads(response)
        if "status" in response and response["status"] == "ok":
            log("{} [INFO] Sent {}".format(str(datetime.now()),len(data["data"])))
        else:
            log("{} [ERROR] {}".format(str(datetime.now()),str(response)))

if __name__ == '__main__':
    data = {
        "id": os.environ["HB_ID"],
        "key": os.environ["HG_KEY"],
        "data": get_from_redis()
    }

    if len(data["data"]) > 0:
        try:
            asyncio.get_event_loop().run_until_complete(
                send_data(data))
        except Exception as e:
            log("{} [ERROR] {}".format(str(datetime.now()),e))
            r = redis.Redis(unix_socket_path='/var/run/redis/redis.sock')
            for item in data["data"]:
                r.set(item["id"], json.dumps(item))
