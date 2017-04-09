import asyncio, base64
from aiohttp import web
from cryptography import fernet
from aiohttp_session import setup as session_setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import database
import mazemap

HTML_base = """
<!doctype html>
<html>
<title>Toilet Finder</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

{text}

</html>
"""[1:-1]

#decoratora:
def handle_html(func):
	async def ret(*args, **kwargs):
		text = await func(*args, **kwargs)
		
		out = web.Response(
			content_type = "text/html",
			text = HTML_base.format(text=text)
		)
		
		return out
	return ret
def using_base(filename):
	with open(f"base/{filename}", "r") as f:
		base = f.read()
	def decorator(func):
		async def ret(request):
			out = await func(request, base)
			return out
		return ret
	return decorator

@handle_html
@using_base("index.html")
async def GET_index(request, base):
	return base.format(text = "index")


@handle_html
async def GET_test(request):
	#session = await get_session(request)
	out = await mazemap.test(request)
	return out


@handle_html
async def GET_mazemap(request):
	#session = await get_session(request)
	#request.query
	
	from random import choice
	toilets = await database.select_toilets(request)
	
	red, blue = [], []
	for i in toilets: choice((red, blue)).append(i)
	
	out  = "%s\n%s" % (
		mazemap.make_marker_chubs(red, color = "red"),
		mazemap.make_marker_chubs(blue, color = "blue")
	)
	
	return mazemap.JS_skeleton.format(code = out)











def add_routes(app):
	#app.router.add_route('POST', '/pv/v1/', handle_v1)
	app.router.add_get('/',      GET_index)
	app.router.add_get('/index', GET_index)
	
	app.router.add_get('/mazemap', GET_mazemap)
	
	app.router.add_get('/mazetest', GET_test)
	
	app.router.add_static(
		'/static/',
		path='static',
		name='static'
	)
	
	fernet_key = fernet.Fernet.generate_key()
	secret_key = base64.urlsafe_b64decode(fernet_key)
	session_setup(app, EncryptedCookieStorage(secret_key))
