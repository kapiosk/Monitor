from datetime import datetime
import subprocess
import os
import json

from influxdb import InfluxDBClient
from dotenv import load_dotenv

load_dotenv()

its = {}

with open('pingList.json') as json_file:
    pcs = json.load(json_file)
    for pc in pcs:
        for ip in pcs[pc]:
            res = subprocess.call(["ping","-c", "1", ip], 
                                  stdout=subprocess.DEVNULL)
            tag = f"{pc} - {ip}"
            if res == 0:
                its[tag] = 1
            else:
                its[tag] = 0

request_body = [{
    "measurement": "PING",
    "tags": {},
    "time": datetime.utcnow().isoformat(),
    "fields": its
}]

client = InfluxDBClient(os.getenv("INFHOST"), "8086", os.getenv("INFUSER"),
                        os.getenv("INFPASS"), os.getenv("INFDB"))
client.write_points(request_body)