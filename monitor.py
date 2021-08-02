from datetime import datetime
import os

import Adafruit_DHT
import psutil
from gpiozero import CPUTemperature
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

# crontab -e
# */1 * * * * cd /home/pi/Development/Monitor && python3 monitor.py

def CheckValue(val):
    return val is not None and val < 200 and val > 15

load_dotenv()

its = {}

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

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
    "time": datetime.utcnow().isoformat(),
    "fields": its
}]
client = InfluxDBClient(url=os.getenv("INFHOST"), token=os.getenv("INFTOKEN"))
write_api = client.write_api(write_options=SYNCHRONOUS)
write_api.write(os.getenv("INFDB"), os.getenv("INFORG"), request_body)