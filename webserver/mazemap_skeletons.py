#https://api.mazemap.com/js/v1.1.1/docs/examples.html#showing-custom-pois

#
JS_head = """
<link rel="stylesheet" href="https://api.mazemap.com/js/v1.2.9/mazemap.min.css">
<script type='text/javascript' src='https://api.mazemap.com/js/v1.2.9/mazemap.min.js'></script>
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


