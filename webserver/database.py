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
async def execute(request, query, fetch=False, params=None):
	if ";" in query:
		raise Exception("Multible queries caught: %s" % query)
	
	app = request.app if hasattr(request, "app") else request
	
	async with app["pool"].acquire() as conn:
		async with conn.cursor() as cur:
			#q = await cur.mogrify(query, params)
			#print(q)
			await cur.execute(query, params)
			if fetch:
				if type(fetch) is int:
					ret = await cur.fetchmany(fetch)
				else:
					ret = await cur.fetchall()
				#print(ret)
				return ret

#premade queries
async def select_tags(request, fetch=True):#(id, name)
	return await execute(request, "SELECT * FROM tags", fetch)

async def select_statuses(request, fetch=True):#(toilet, dt, status)
	return await execute("SELECT * FROM status ORDER BY dt ASC", fetch)

async def select_statuses_by_toilet(request, toilet, fetch=True):#(toilet, dt, status)
	return await execute("SELECT * FROM status WHERE toilet=%s ORDER BY dt ASC", fetch, params=(int(toilet),))

async def select_toilets(request, fetch=True):#(id, lat, lng, name, poi_id)
	return await execute(request, "SELECT * FROM toilets ORDER BY id DESC", fetch)

async def select_toilet(request, toiletid):#(id, lat, lng, name, poi_id)
	return await execute(request, f"SELECT * FROM toilets WHERE id={int(toiletid)}", 1)

async def select_toilet_statuses(request, fetch=True):#(id, lat, lng, name, status, dt)
	return await execute(request, "SELECT * FROM toilet_status", fetch)

async def select_toilet_status(request, toiletid):#(id, lat, lng, name, status, dt)
	return await execute(request, f"SELECT * FROM toilet_status WHERE id={int(toiletid)}", 1)

async def select_toilets_by_tagnames(request, tagnames, fetch=True):#todo:test
	tagnames = tuple(map(str, tags))
	return await execute(request,"SELECT * FROM toilets as s WHERE s.id IN (SELECT t.toilet FROM toilet_tags as t JOIN tags ON tags.id = t.tag WHERE tags.name IN %s)", fetch, params=(tagnames,))
	
async def select_toilet_statuses_by_tagnames(request, tagnames, fetch=True):#todo:test
	tagnames = tuple(map(int, tags))
	return await execute(request,"SELECT * FROM toilet_status as s WHERE s.id IN (SELECT t.toilet FROM toilet_tags as t JOIN tags ON tags.id = t.tag WHERE tags.name IN %s)", fetch, params=(tagnames,))
	
async def select_toilet_statuses_by_tags(request, tags, fetch=True):#todo:test
	tags = tuple(map(int, tags))
	return await execute(request,"SELECT * FROM toilet_status as s WHERE s.id IN (SELECT t.toilet FROM toilet_tags AS t WHERE t.tag IN %s)", fetch, params=(tags,))

async def insert_toilet(request, lat, lng, name, poi_ID):
	return await execute(request, "INSERT INTO toilets (lat, lng, name, poi_id) VALUES (%s, %s, %s, %s) RETURNING id", 1, params=(lat, lng, name, poi_ID))

async def delete_toilets(request, IDs):
	await execute(request, "DELETE FROM toilets WHERE id in %s", params=(tuple(IDs),))

async def select_reports(request):#(id, desc, toilet(id))
	return await execute(request, "SELECT * FROM reports", True)
async def insert_report(request, desc, toilet):
	return await execute(request, "INSERT INTO reports (description, toilet) VALUES (%s, %s) RETURNING id", 1, params=(str(desc), int(toilet)))
async def delete_report(request, ID):
	await execute(request, f"DELETE FROM reports WHERE id = {int(ID)}")

async def insert_tag(request, name):
	return await execute(request, "INSERT INTO tags (name) VALUES (%s) RETURNING id", 1, params=(name,))

async def delete_tags(request, tags):
	await execute(request, "DELETE FROM tags WHERE id in %s", params=(tuple(tags),))

async def insert_user(request, uname, bcrypt_hash, admin=False):
	admin = bool(admin)
	await execute(request, "INSERT INTO users (uname, bcrypt_hash, admin) VALUES (%s, %s, %s)", params=(uname, bcrypt_hash, admin))

async def update_user_password(request, uname, bcrypt_hash):
	await execute(request, "UPDATE users SET bcrypt_hash=%s WHERE uname=%s", params=(bcrypt_hash, uname))
async def select_user(request, uname):#[i]=(id, uname, bcrypt_hash, admin?)
	return await execute(request, "SELECT * FROM users WHERE uname = %s", 1, params=(uname,))
	
