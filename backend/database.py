import asyncio, aiopg
from time import strftime
from MQTT import QOS_1

#queries:
async def update_door_state(conn, topic, data):#open or closed
	toiletID = int(topic.split("/")[1])
	state = int(data)
	time = strftime("TIMESTAMP WITH TIME ZONE '%Y-%m-%d %H:%M:%S+01'")
	
	async with conn.cursor() as cur:
		#await cur.execute(f"UPDATE doors SET state = {state} WHERE id = {ID}")
		await cur.execute(f"INSERT INTO status (toilet, dt, status)"
						+ f"VALUES ({toiletID}, {time}, {state})")
		#await ret = cur.fetchall()


async def update_door_sensor(conn, topic, data):#dead or alive
	ID = int(topic.split("/")[1])
	state = data == "alive"
	
	async with conn.cursor() as cur:
		await cur.execute(f"UPDATE doors SET alive = {state} WHERE id = {ID}")
		#await ret = cur.fetchall()



#main coroutine:
async def main_coro(mqtt, dbHost, dbName, dbUser, dbPasswd):
	dsn = f"dbname={dbName} user={dbUser} password={dbPasswd} host={dbHost}"
	async with aiopg.create_pool(dsn) as pool:
		async with pool.acquire() as conn:
			
			queue = []
			def make_coro_enqueuer(coro):
				def ret(topic, data):
					queue.append(( coro, (conn, topic, data), (,) ))
					#queue.append((coro, args, kwargs))
				return ret
			
			
			await mqtt.subscribe("door/+/state",  make_coro_enqueuer(update_door_state),  qos=QOS_1)
			await mqtt.subscribe("door/+/sensor", make_coro_enqueuer(update_door_sensor), qos=QOS_1)
			
			
			while 1:
				while queue:
					coro, args, kwargs = queue.pop(0)
					await func(*args, **kwargs)
				
				await asyncio.sleep(1)


