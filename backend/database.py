import asyncio, aiopg, datetime
from mqtt_client import QOS_1

#queries:
async def update_door_state(conn, topic, data):#open or closed
	toiletID = int(topic.split("/")[1])
	state = {True:1,False:2}[bool(int(data))]
	time = datetime.datetime.now()
	
	async with conn.cursor() as cur:
		await cur.execute("INSERT INTO status (toilet, dt, status)"
						+ "VALUES (%s, %s, %s)", (toiletID, time, state))
		#await ret = cur.fetchall()

async def update_door_sensor(conn, topic, data):#dead or alive
	toiletID = int(topic.split("/")[1])
	state = {True:2, False:0}[data == "alive"]
	time = datetime.datetime.now()
	
	async with conn.cursor() as cur:
		await cur.execute("INSERT INTO status (toilet, dt, status)"
						+ "VALUES (%s, %s, %s)", (toiletID, time, state))
		#await ret = cur.fetchall()

#main coroutine:
async def main_coro(mqtt, dbHost, dbName, dbUser, dbPasswd):
	dsn = f"dbname={dbName} user={dbUser} password={dbPasswd} host={dbHost}"

	async with aiopg.create_pool(dsn) as pool:
		async with pool.acquire() as conn:
			
			queue = []
			def make_coro_enqueuer(coro):
				def ret(topic, data):
					queue.append(( coro, (conn, topic, data), () ))
					#queue.append((coro, args, kwargs))
				return ret
			
			
			await mqtt.subscribe("door/+/state",  make_coro_enqueuer(update_door_state),  qos=QOS_1)
			await mqtt.subscribe("door/+/sensor", make_coro_enqueuer(update_door_sensor), qos=QOS_1)
			
			
			while 1:
				while queue:
					coro, args, kwargs = queue.pop(0)
					await func(*args, **kwargs)
				
				await asyncio.sleep(1)


