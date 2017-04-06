import asyncio
from urllib.parse import quote_plus
import database

#https://api.mazemap.com/js/v1.1.1/docs/examples.html#showing-custom-pois
JS_skeleton = """
<link rel="stylesheet" href="https://api.mazemap.com/js/v1.1.1/mazemap.min.css">
<script type='text/javascript' src='https://api.mazemap.com/js/v1.1.1/mazemap.min.js'></script>
<style>
	body {{ margin: 0; }}
	#mazemap-container {{
		width: 100vw;
		height: 100vh;
	}}
</style>

<div id='mazemap-container'></div>

<script>
var map = Maze.map('mazemap-container', {{}});

{code}
</script>
"""[1:-1]


JS_map_chub = """
Maze.marker([{lng}, {lat}], {{
	icon: Maze.icon.chub({{
		color: '{color}',
		glyph: '{glyph}'
	}})
}}).addTo(map);
"""[1:-1]


#params:
def param_dest_toilet_poi(toiletID):
	out = [
		"campusid=1",
		"desttype=poi",
		f"dest={toiletid}"
	]
	return "&".join(out)

def param_zoom(level=18.5):#between 1 and 22
	return f"zoom={level}"


#make:
async def test(request):
	import random
	
	points = []
	toilets = await database.select_toilets(request)
	for ID, lat, lng, name, poi_id in toilets:
		points.append(JS_map_chub.format(lat=lat, lng=lng, color=random.choice(("blue", "red")), glyph="human-male-female"))
	
	return JS_skeleton.format(code = ("\n".join(points)))
	


#left for when i need to populate the database with more data
async def do_once(app):
	return
	return
	return
	
	import json
	d = json.load(open("download.json", "r"))
	for i in d["pois"]:
		if type(i["geometry"]["coordinates"][0]) is not float: continue
		
		lat = i["geometry"]["coordinates"][0]
		lng = i["geometry"]["coordinates"][1]
		name = i["title"]
		poi_ID = i["poiId"]
		
		await database.insert_toilet(app, lat, lng, name, poi_ID)

