#!/usr/bin/env python3
import asyncio, configparser, sys, os, aiopg
from aiohttp import web
from server import add_routes


default_config = """
[postgres]
host=klient.pbsds.net
dbname=shitbase
user=frontend
password=bestePassordet

"""[1:-1]#removes first and last newline


def main(ini):
	async def init_pg(app):
		#engine = await aiopg.sa.create_engine(
		#	database = ini.get("postgres", "dbname"),
		#	user     = ini.get("postgres", "user"),
		#	password = ini.get("postgres", "password"),
		#	host     = ini.get("postgres", "host"),
		#	loop     = app.loop
		#)
		#app['engine'] = engine
		dbHost   = ini.get("postgres", "host")
		dbName   = ini.get("postgres", "dbname")
		dbUser   = ini.get("postgres", "user")
		dbPasswd = ini.get("postgres", "password")
		
		dsn = f"dbname={dbName} user={dbUser} password={dbPasswd} host={dbHost}"
		pool = await aiopg.create_pool(dsn)
		app["pool"] = pool
		
	async def close_pg(app):
		app['pool'].close()
		await app['pool'].wait_closed()
	
	app = web.Application()
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
