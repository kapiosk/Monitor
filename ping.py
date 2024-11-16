from datetime import datetime, timezone
import re
import subprocess
import os
import json
import time
import urllib.request
from timeit import default_timer as timer

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

load_dotenv()

its = {}

with open(os.getenv("PINGFILE")) as json_file:
    pcs = json.load(json_file)

for pc, site in pcs["sites"].items():
    try:
        start = timer()
        with urllib.request.urlopen(site) as response:
            status = response.status

            if status == 200:
                elapsedMS = (timer() - start) * 1000
                its[pc] = elapsedMS
    except Exception:
        time.sleep(1)

for pc, ip in pcs["ping"].items():
    try:
        out = subprocess.check_output(["ping", "-c", " 1", ip]).decode("utf-8")
        elapsedMS = float(re.search("time=(.*)ms", out).group(1))
        its[pc] = elapsedMS
    except Exception:
        time.sleep(1)

request_body = [{
    "measurement": "Network",
    "tags": {},
    "time": datetime.now(timezone.utc).isoformat(),
    "fields": its
}]

host = os.getenv("INFHOST")
token = os.getenv("INFTOKEN")
bucket = os.getenv("INFBUCKET")
org = os.getenv("INFORG")
client = InfluxDBClient(url=host, token= token)
write_api = client.write_api(write_options=SYNCHRONOUS)
write_api.write(bucket, org ,request_body)
