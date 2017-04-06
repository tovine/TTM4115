import asyncio, configparser
from mqtt_client import MQTT
from database import main_coro

default_config = """
[MQTT]
broker = mqtt://backend:hunter2@klient.pbsds.net:1883
certfile = None

[postres]
host=klient.pbsds.net
dbname=shitbase
user=backend
password=yolotopkeksuper1337masterrace

"""[1:-1]#removes first and last newline


def main(ini):
	loop = asyncio.get_event_loop()
	
	broker   = ini.get("MQTT", "broker")
	certfile = ini.get("MQTT", "certfile")
	
	mqtt = MQTT(loop, broker)
	
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
