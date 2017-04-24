#!/usr/bin/env python3
import asyncio, configparser, sys, os, aiopg, base64
from aiohttp import web
from server import add_routes, create_session_secret
from database import init_pg, close_pg
from mazemap import do_once


default_config = f"""
[postgres]
host=klient.pbsds.net
dbname=shitbase
user=frontend
password=bestePassordet

[sessions]
cookie_secret = {base64.b64encode(create_session_secret()).decode('UTF-8')}
session_idle_timeout = 1200
cached_page_timeout = 10
"""[1:-1]#removes first and last newline


def main(ini):
	app = web.Application()
	app["ini"] = ini
	
	app.on_startup.append(init_pg)
	app.on_startup.append(do_once)
	app.on_cleanup.append(close_pg)
	
	add_routes(app, base64.b64decode(ini.get("sessions", "cookie_secret").encode("UTF-8")))#ew
	
	web.run_app(app)

if __name__ == "__main__":
	configfile = "config.ini"
	args = sys.argv[1:]
	while args:
		if args[0] == "--config":
			args.pop(0)
			configfile = args.pop(0)
		elif args[0] == "--no-cache":
			import server
			server.DOCACHE = False
			args.pop(0)
		else:
			break
	
	if not os.path.exists(configfile):
		with open(configfile, "w") as f:
			f.write(default_config)
	
	ini = configparser.ConfigParser()
	with open(configfile, "r") as f:
		ini.read_file(f)
	
	main(ini)
