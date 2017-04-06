#!/usr/bin/env python3
import asyncio, configparser, sys, os, aiopg
from aiohttp import web
from server import add_routes
from database import init_pg, close_pg


default_config = """
[postgres]
host=klient.pbsds.net
dbname=shitbase
user=frontend
password=bestePassordet

"""[1:-1]#removes first and last newline


def main(ini):
	app = web.Application()
	app["ini"] = ini
	
	app.on_startup.append(init_pg)
	app.on_cleanup.append(close_pg)
	
	add_routes(app)
	
	web.run_app(app)

if __name__ == "__main__":
	configfile = sys.argv[1] if len(sys.argv) > 1 else "config.ini"
	if not os.path.exists(configfile):
		with open(configfile, "w") as f:
			f.write(default_config)
	
	ini = configparser.ConfigParser()
	with open(configfile, "r") as f:
		ini.read_file(f)
	
	main(ini)
