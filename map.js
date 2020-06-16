
var map;

function initmap(){

map = new mapboxgl.Map({
    container: 'map',
    style: 'https://api.maptiler.com/maps/positron/style.json?key=DnTMUKM1IaBfW6AjV7bn',
    zoom: 15.5,
	pitch: 60, // pitch in degrees
	bearing: -60, // bearing in degrees
    center: [6.661585209069443, 51.91879773273479]
});

map.on('load', function () {
	map.addControl(new mapboxgl.NavigationControl());

    var LegendEl = document.getElementById('legend');
    LegendEl.style.display = 'block';
});

map.on('styledata', function () {

    map.addSource('bomen', {
        'type': 'vector',
        'tiles': [
          'http://leda.geodan.nl:1500/bomen_mvt/{z}/{x}/{y}'
        ],
        'minzoom': 8,
        'maxzoom': 14
      });
      map.addLayer({
          "id": "bomen",
          "type": "fill-extrusion",
          "source": "bomen",
          'source-layer': 'bomen',
          'paint': {
              'fill-extrusion-color': [
                  'match',
                  ['get', 'elementtype'],
                  'Solitaire boom', '#42f5b6',
                  'Bomengroep', '#0B5345',
                  'Bomenrij', '#F4D03F',
                  'Houtwal', '#6E2C00',
                  /* other */ '#ccc'
              ],
              'fill-extrusion-opacity': 0.6,
              "fill-extrusion-height": ['get', "hoogte"]
          }
      });
    

	
    map.addSource('landschapselementen', {
	  'type': 'vector',
	  'tiles': [
		'http://leda.geodan.nl:1500/landschapselementen_mvt/{z}/{x}/{y}'
	  ],
	  'minzoom': 8,
	  'maxzoom': 14
    });
    map.addLayer({
        "id": "landschapselementen",
        "type": "fill-extrusion",
        "source": "landschapselementen",
		'source-layer': 'landschapselementen',
        'paint': {
            'fill-extrusion-color': [
				'match',
                ['get', 'elementtype'],
                'Solitaire boom', '#42f5b6',
                'Bomengroep', '#0B5345',
                'Bomenrij', '#F4D03F',
                'Houtwal', '#6E2C00',
                'Heg', '#43FF33',
                'Poel', '#0CFDFE',
                /* other */ '#ccc'
            ],
            'fill-extrusion-opacity': 0.6,
			"fill-extrusion-height": [
				'match',
                ['get', 'elementtype'],
                'Solitaire boom', 1,
                'Bomengroep', 1,
                'Bomenrij', 1,
                'Houtwal', 1,
                'Heg', ['get', 'hoogte'],
                'Poel', 0,
                /* other */ 0
            ]
		}
	});

});

map.on('click', 'bomen', function (e) {
    var prop = e.features[0].properties;
	prop.hoogte = Math.round(prop.hoogte * 10) / 10;
	prop.avg_height = Math.round(prop.avg_height * 10) / 10;
    var htmlstring = '<h2>' + prop.elementtype + '</h2><p>Element id: ' + prop.elementid + 
		'<br>Aantal bomen: ' + prop.aantalbomen + '<br>Gemiddelde hoogte: ' + prop.avg_height + 
		' meter</p><p><h3>Boomgegevens:</h3> Boomregister id: ' + prop.tree_id + 
		'<br>Hoogte: ' + prop.hoogte + ' meter</p>' +
        '<a class="navbtn openbtn" style="" onclick="openNav(\'' + prop.elementtype + '\', \'' + prop.elementid + '\')">Toon geschiedenis</a>';
    new mapboxgl.Popup().setLngLat(e.lngLat).setHTML(htmlstring).addTo(map);
});
map.on('click', 'landschapselementen', function (e) {
    var prop = e.features[0].properties;
    console.log(prop);
	prop.hoogte = Math.round(prop.hoogte * 10) / 10;
    var htmlstring = '<h2>' + prop.elementtype + '</h2><p>Element id: ' + prop.elementid + 
        '<br>Gemiddelde hoogte: ' + prop.hoogte + ' meter<br>Aantal bomen: ' + prop.aantalbomen +
        '<br>Onderhoudsstatus: ' + prop.onderhoudsstatus + '<br>In onderzoek: ' + prop.inonderzoek +
        '<br>Bronhouder: ' + prop.bronhouder + '</p>' +
        '<a class="navbtn openbtn" style="" onclick="openNav(\'' + prop.elementtype + '\', \'' + prop.elementid + '\')">Toon geschiedenis</a>';
    new mapboxgl.Popup().setLngLat(e.lngLat).setHTML(htmlstring).addTo(map);
});

var layerList = document.getElementById('menu');
var inputs = layerList.getElementsByTagName('input');
for (var i = 0; i < inputs.length; i++) {
	inputs[i].onclick = switchLayer;
}
}

function switchLayer(layer) {
	map.setStyle('https://api.maptiler.com/maps/' + layer.target.id + '/style.json?key=DnTMUKM1IaBfW6AjV7bn');
}
 
