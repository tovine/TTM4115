import asyncio
from aiohttp import web
import database

async def GET_index(request):
	#name = request.match_info.get('name', "Anonymous")
	#text = "Hello, " + name
	d = await database.select_tags(request)
	return web.Response(text=str(d))










def add_routes(app):
	#app.router.add_route('POST', '/pv/v1/', handle_v1)
	app.router.add_get('/', GET_index)
	
