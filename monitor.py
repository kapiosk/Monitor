from datetime import datetime
import os

import Adafruit_DHT
import psutil
from gpiozero import CPUTemperature
from influxdb import InfluxDBClient
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
client = InfluxDBClient(os.getenv("INFHOST"), "8086", os.getenv("INFUSER"),
                        os.getenv("INFPASS"), os.getenv("INFDB"))
client.write_points(request_body)