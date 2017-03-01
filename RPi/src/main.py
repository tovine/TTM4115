#!/usr/bin/env python3
import sys, os, asyncio, configparser

from mqtt_client import main_coro


default_config = """
[MQTT]
broker=mqtt://test.mosquitto.org/

[sensor]

"""

async def wakeup():
	while 1:
		#print("test")
		await asyncio.sleep(0.5)


def main():
	loop = asyncio.get_event_loop()
	
	tasks = [
		main_coro(),
		wakeup()
	]
	
	#waits untill all tasks are complete
	loop.run_until_complete(asyncio.wait(tasks))
	loop.close()



if __name__ == '__main__':
	configfile = sys.argv[1] if len(sys.argv) > 1 else "config.ini"
	if not os.path.exists(configfile):
		with open(configfile, "w") as f:
			f.write(default_config)
	
	ini = configparser.configparser(configfile)
	
	mqtt_broker = ini.get("MQTT", "broker")
	mqtt_port = ini.get("MQTT", "broker")
	
	ini = configparser.configparser("")
	
	main()