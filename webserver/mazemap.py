import asyncio
from urllib.parse import quote_plus
import database
from mazemap_skeletons import *

#iterator definitions:
#	toilets[i] = (ID, lat, lng, name, poi_id)


async def test(request):
	from random import choice
	
	if hasattr(test, "points"):
		toilets = []
		for i in test.points[:100]:
			toilets.append((None, i[0], i[1], None, None))
	else:
		toilets = await database.select_toilets(request)
	
	ids = []
	for key, val in request.query.items():
		if key=="id": ids.append(int(val))
	if ids:
		toilets = tuple(i for i in toilets if i[0] in ids)
	
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
	print("mazemap.do_once")
	
	#await database.execute(app, "UPDATE users SET admin=true WHERE uname='pbsds'")
	
	import json, urllib.request
	#data = urllib.request.urlopen("http://api.mazemap.com/api/pois/?campusid=1&srid=4326&typeid=9").read()
	#with open("pois.json", "w") as f:
	#	f.write(data)
	data = open("pois.json", "r")
	d = json.load(data)
	test.points = []
	ids = set()
	for i in d["pois"]:
		#if type(i["geometry"]["coordinates"][0]) is not float: continue
		
		#if i["geometry"]["type"] != "Point":
			#print(i["title"], i["poiId"])
			#print(i)
			#test.points.extend(i["geometry"]["coordinates"][0])
			#continue
		
		if i["geometry"]["type"] == "Point":
			lat = i["geometry"]["coordinates"][0]
			lng = i["geometry"]["coordinates"][1]
		else:
			continue
			lat = 0
			lng = 0
			for a, b in i["geometry"]["coordinates"][0]:
				lat += a
				lng += b
			lat /= len(i["geometry"]["coordinates"][0])
			lng /= len(i["geometry"]["coordinates"][0])
			
		name = i["title"]
		poi_ID = i["poiId"]
		if poi_ID not in ids:
			test.points.append((lat, lng))
			ids.add(poi_ID)
		
		print(lat, lng, name, poi_ID)
		print()
		#return
		
		#await database.insert_toilet(app, lat, lng, name, poi_ID)

