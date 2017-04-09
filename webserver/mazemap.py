import asyncio
from urllib.parse import quote_plus
import database
from mazemap_skeletons import *

#iterator definitions:
#	toilets[i] = (ID, lat, lng, name, poi_id)


async def test(request):
	from random import choice
	toilets = await database.select_toilets(request)
	
	red, blue = [], []
	for i in toilets: choice((red, blue)).append(i)
	
	out  = "%s\n%s" % (
		make_marker_chubs(red, color = "red"),
		make_marker_chubs(blue, color = "blue")
	)
	return JS_skeleton.format(code = out)

def make_marker_chubs(toilets, color = "blue", glyph = "human-male-female"):
	points = []
	for ID, lat, lng, name, poi_id in toilets:
		points.append(JS_map_marker_chub.format(
			lat = lat,
			lng = lng,
			color = color,
			glyph = glyph
		))
	
	return "\n".join(points)


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

