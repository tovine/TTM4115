#https://api.mazemap.com/js/v1.1.1/docs/examples.html#showing-custom-pois

#
JS_head = """
<link rel="stylesheet" href="https://api.mazemap.com/js/v1.2.10/mazemap.min.css">
<script type='text/javascript' src='https://api.mazemap.com/js/v1.2.10/mazemap.min.js'></script>
<script>window.L = window.Maze;</script>
<script src='https://api.mazemap.com/js/v1.2.10/example-plugins/Leaflet.Icon.Pulse/L.Icon.Pulse.js'></script>
<link href="https://api.mazemap.com/js/v1.2.10/example-plugins/Leaflet.Icon.Pulse/L.Icon.Pulse.css" rel="stylesheet">
"""[1:-1]

#
JS_body = """
<div id='mazemap-container'></div>

<script>
var map = Maze.map('mazemap-container', {{campusloader: false}});
Maze.Instancer.getCampus(1).then( function (campus) {{
	map.fitBounds(campus.getBounds());
	campus.addTo(map).setActive().then( function() {{
			map.setZLevel(1);
			map.getZLevelControl().show();
	}});
}});

{code}
</script>
"""[1:-1]

#
JS_skeleton = f"""
{JS_head}
<style>
	body {{{{ margin: 0; }}}}
	#mazemap-container {{{{
		width: 100vw;
		height: 100vh;
	}}}}
</style>

{JS_body}
"""[1:-1]

#
JS_map_marker_chub = """
Maze.marker([{lng}, {lat}], {{
	icon: Maze.icon.chub({{
		color: '{color}',
		glyph: '{glyph}'
	}})
}}).addTo(map);
"""[1:-1]

#
JS_map_locator = """
var pulsingMarker = null;
map.on('locationfound', function(ev) {
	console.log('locationfound');
	
	if(pulsingMarker){
		pulsingMarker.setLatLng(ev.latlng);
		
	}else{
		var pulsingIcon = Maze.icon.pulse({iconSize:[20, 20],color:'red'});
		pulsingMarker = Maze.marker(ev.latlng, {
			icon: pulsingIcon
		}).addTo(map);
	}
});
map.locate({ setView: false, enableHighAccuracy: true });
"""[1:-1]

