import asyncio, configparser
from mqtt_client import MQTT
from database import main_coro

default_config = """
[MQTT]
broker = test.mosquitto.org
port = default
certfile = None

[postres]
host=127.0.0.1
dbname=aiopg
user=aiopg
password=hunter2

"""[1:-1]#removes first and last newline


def main(ini):
	loop = asyncio.get_event_loop()
	
	broker   = ini.get   ("MQTT", "broker")
	port     = ini.getint("MQTT", "port") if not ini.get("MQTT", "port")=="default" else 1883
	certfile = ini.get   ("MQTT", "certfile")
	
	mqtt = MQTT(loop, broker, port)
	
	dbHost   = get("postgres", "host")
	dbName   = get("postgres", "dbname")
	dbUser   = get("postgres", "user")
	dbpasswd = get("postgres", "password")
	
	#run:
	tasks = [
		mqtt.main_coro(),
		mqtt.queue_coro(),
		main_coro(mqtt, dbHost, dbName, dbUser, dbPasswd),
	]
	
	loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == "__main__":
	configfile = sys.argv[1] if len(sys.argv) > 1 else "config.ini"
	if not os.path.exists(configfile):
		with open(configfile, "w") as f:
			f.write(default_config)
	
	ini = configparser.ConfigParser()
	with open(configfile, "r") as f:
		ini.read_file(f)
	
	main(ini)
