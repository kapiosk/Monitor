from datetime import datetime, timezone
import os

import adafruit_dht
import board
import psutil
from gpiozero import CPUTemperature
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

def CheckValue(val):
    return val is not None and val < 200 and val > 15

load_dotenv()

its = {}

dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

temperature = dhtDevice.temperature
humidity = dhtDevice.humidity

if CheckValue(temperature):
    its.update(Temperature=temperature)

if CheckValue(humidity):
    its.update(Humidity=humidity)

CPUTemp = CPUTemperature().temperature
if CheckValue(CPUTemp):
    its.update(CPUTemperature=CPUTemp)

its.update(CPUPercent=psutil.cpu_percent())

request_body = [{
    "measurement": "DHT22",
    "tags": {},
    "time": datetime.now(timezone.utc).isoformat(),
    "fields": its
}]

client = InfluxDBClient(url=os.getenv("INFHOST"), token=os.getenv("INFTOKEN"))
write_api = client.write_api(write_options=SYNCHRONOUS)
write_api.write(os.getenv("INFBUCKET"), os.getenv("INFORG"), request_body)
