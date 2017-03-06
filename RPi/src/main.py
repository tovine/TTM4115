#!/usr/bin/env python3
import sys, os, asyncio, configparser
from mqtt_client import MQTT

DEBUG = False
default_config = """
[MQTT]
broker = test.mosquitto.org
port = default
certfile = None

[sensor]

"""[1:]

async def init(mqtt):
	#while 1:
	#	await asyncio.sleep(0.5)
	#await mqtt.publish("test", "spis meg")
	print("test1")
	await mqtt.subscribe("$SYS/broker/uptime", callback=print)
	print("test2")

def main(ini):
	loop = asyncio.get_event_loop()
	
	broker   = ini.get   ("MQTT", "broker")
	port     = ini.getint("MQTT", "port") if not ini.get("MQTT", "port")=="default" else 1883
	certfile = ini.get   ("MQTT", "certfile")
	
	mqtt = MQTT(loop, broker, port)
	
	#sensor_topic = 
	
	
	
	
	#run:
	tasks = [
		mqtt.main_coro(debug=DEBUG, stopLoop=True),
		mqtt.queue_coro(),
		init(mqtt)
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