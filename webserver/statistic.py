import time, datetime, asyncio
from statistics import mean#standard library
import database


#decorators
def memoize_coro(func):
	mem = {}
	async def ret(request, *args, **kwargs):
		k = (args, kwargs)
		if k not in mem:
			pass
		elif time.time() - mem[k][0] > 60:
			pass
		else:
			return mem[k][1]
		
		out = await func(request, *args, **kwarg)
		mem[k] = (time.time(), out)
		return out
	return ret

@memoize_coro
async def toilet_availability(request, toilet):#between 0 and 1, 1 being always
	available = 0
	unavailable = 0
	
	statuses = await database.select_statuses_by_toilet(request, toilet)
	prev_stat = statuses[0][2]
	prev_dt = statuses[0][1]
	statuses.pop(0)
	statuses.append((None, datetime.datetime.now(), statuses[-1][2]))
	for i, (ID, dt, status) in enumerate(statuses):
		if prev_stat == 1:#unavailable
			unavailable += (dt - prev_dt).total_seconds()
		elif prev_stat == 2:#available
			available += (dt - prev_dt).total_seconds()
		
		prev_stat = status
		prev_dt = dt
		
		if not i%1000:
			await asyncio.sleep(0)#let's not block the server eh?
	
	
	return available / (available + unavailable)


