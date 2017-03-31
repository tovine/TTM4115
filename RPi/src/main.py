#!/usr/bin/env python3
import sys, os, asyncio, configparser
from mqtt_client import MQTT
#import sensor

DEBUG = False
default_config = """
[MQTT]
broker = test.mosquitto.org
port = default
certfile = None

[sensor]
ID = 0
GPIO_BCM_Port = 4

"""[1:-1]#removes first and last newline

async def init(mqtt):
	print("Subscribing to \"$SYS/broker/uptime\"... ", end="")
	await mqtt.subscribe("$SYS/broker/uptime", callback=print)
	print("Done!")

def main(ini):
	loop = asyncio.get_event_loop()
	
	broker   = ini.get   ("MQTT", "broker")
	port     = ini.getint("MQTT", "port") if not ini.get("MQTT", "port")=="default" else 1883
	certfile = ini.get   ("MQTT", "certfile")
	
	mqtt = MQTT(loop, broker, port)
	
	sensorid = ini.getint("sensor", "ID")
	gpio_port = ini.getint("sensor", "GPIO_BCM_Port")
	
	#run:
	tasks = [
		mqtt.main_coro(debug=DEBUG, stopLoop=True),
		mqtt.queue_coro(),
		sensor.maincoro(loop, mqtt, sensorid, gpio_port),
		#init(mqtt)
	]
	
	loop.run_until_complete(asyncio.gather(*tasks))#waits untill all tasks are complete
	loop.close()


if __name__ == '__main__':
	configfile = sys.argv[1] if len(sys.argv) > 1 else "config.ini"
	if not os.path.exists(configfile):
		with open(configfile, "w") as f:
			f.write(default_config)
	
	ini = configparser.ConfigParser()
	with open(configfile, "r") as f:
		ini.read_file(f)
	
	main(ini)