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

#html decorator:
def handle_html(func):
	async def ret(*args, **kwargs):		
		out = await func(*args, **kwargs)
		out.content_type = "text/html"
		
		out.body
		
		out.body = HTML_base.format(text=str(out.body, "utf-8")).encode("utf-8")
		
		return out
	return ret


@handle_html
async def GET_index(request):
	d = "test"
	
	return web.Response(text=str(d))


@handle_html
async def GET_test(request):
	#session = await get_session(request)
	out = await mazemap.test(request)
	
	return web.Response(text=out)











def add_routes(app):
	#app.router.add_route('POST', '/pv/v1/', handle_v1)
	app.router.add_get('/',      GET_index)
	app.router.add_get('/index', GET_index)
	
	app.router.add_get('/mazetest', GET_test)
	
	fernet_key = fernet.Fernet.generate_key()
	secret_key = base64.urlsafe_b64decode(fernet_key)
	session_setup(app, EncryptedCookieStorage(secret_key))
