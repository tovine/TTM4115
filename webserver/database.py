import asyncio, aiopg

#init:
async def init_pg(app):
	ini = app["ini"]
	
	dbHost   = ini.get("postgres", "host")
	dbName   = ini.get("postgres", "dbname")
	dbUser   = ini.get("postgres", "user")
	dbPasswd = ini.get("postgres", "password")
	
	dsn = f"dbname={dbName} user={dbUser} password={dbPasswd} host={dbHost}"
	
	pool = await aiopg.create_pool(dsn, loop = app.loop)
	
	app["pool"] = pool
async def close_pg(app):
	app['pool'].close()
	await app['pool'].wait_closed()	

#execute a direct query
async def execute(request, query, fetch=False):
	app = request.app if hasattr(request, "app") else request
	
	async with app["pool"].acquire() as conn:
		async with conn.cursor() as cur:
			await cur.execute(query)
			if fetch:
				if type(fetch) is int:
					ret = await cur.fetchmany(fetch)
				else:
					ret = await cur.fetchall()
				#print(ret)
				return ret

#premade queries
async def select_tags(request, fetch=True):#(id, name)
	ret = await execute(request, f"SELECT * FROM tags", fetch)
	return ret

async def select_toilets(request, fetch=True):#(id, lat, lng, name, poi_id)
	ret = await execute(request, f"SELECT * FROM toilets ORDER BY id DESC", fetch)
	return ret

async def select_toilet(request, toiletid):#(id, lat, lng, name, poi_id)
	ret = await execute(request, f"SELECT * FROM toilets WHERE id={toiletid}", 1)
	return ret


async def select_toilet_statuses(request, fetch=True):#(id, lat, lng, name, status, dt)
	ret = await execute(request, f"SELECT * FROM toilet_status", fetch)
	return ret

async def select_toilet_status(request, toiletid):#(id, lat, lng, name, status, dt)
	ret = await execute(request, f"SELECT * FROM toilet_status WHERE id={toiletid}", 1)
	return ret

async def select_toilets_by_tagnames(request, tagnames, fetch=True):#todo:test
	tags = ", ".join(map(repr, tagnames))
	ret = await execute(request, f"SELECT * FROM toilets t WHERE t.id IN (SELECT tags.id FROM tags WHERE tags.name IN ({tags}))", fetch)
	return ret
	
async def select_toilet_statuses_by_tagname(request, tagnames, fetch=True):#todo:test
	tags = ", ".join(map(repr, tagnames))
	ret = await execute(request, f"SELECT * FROM toilet_status t WHERE t.id IN (SELECT tags.id FROM tags WHERE tags.name IN ({tagname}))", fetch)
	return ret

async def insert_toilet(request, lat, lng, name, poi_ID):
	await execute(request, f"INSERT INTO toilets (lat, lng, name, poi_id) VALUES ({lat}, {lng}, '{name}', {poi_ID})")



