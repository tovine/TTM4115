import asyncio, aiopg



#ech
async def template(request):
	async with request.app["pool"].acquire() as conn:
		async with conn.cursor() as cur:
			await cur.execute(f"SELECT")
			ret = await cur.fetchall()
			return ret

async def get_tags(request):
	async with request.app["pool"].acquire() as conn:
		async with conn.cursor() as cur:
			await cur.execute(f"SELECT * FROM tags")
			ret = await cur.fetchall()
			print(ret)
			return ret
