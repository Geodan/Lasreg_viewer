var current_elementid;

function openNav(elementtype, elementid) {
  closeNav();
  current_elementid = elementid;
  document.getElementById("mySidenav").style.width = "300px";
  document.getElementById("mySidenav").style.paddingLeft = "10px";
  document.getElementById("historyH").innerHTML = '<h2 style="padding: 0px; margin: 0px;">Geschiedenis van:</h2><h2 style="padding: 0px; margin: 0px;">' + 
  	elementtype + '</h2><I>' + elementid + '</I><br>';
  fetch("https://saturnus.geodan.nl/lasreg/geschiedenis/" + elementid)
		.then(res => res.json()).then((data) => {
			for(var i = 0; i < data.length; i++) {
				var obj = data[i];
				document.getElementById("navbox").insertAdjacentHTML(
					'beforeend', 
					'<h3 style="padding: 0px; margin: 0px;">' + obj.type + '</h3><font size="-1"><B>auteur:</B> <I>' + obj.author + '</I><br><B>gevalideerd:</B> ' + obj.validated + 
					'<br><B>tijd:</B> <I>' + obj.tijd + '</I></font><br>' + obj.description + '<br><br>'
				);
			}
		});
}

function maak_opmerking() {
	fetch("https://saturnus.geodan.nl/lasreg/opmerking/" + current_elementid + '/' + document.getElementById("type_opm").value + '/' + 
	document.getElementById("naam").value + '/' + document.getElementById("opmerking").value)
		.then(res => res.json()).then((data) => {
			document.getElementById("navbox").innerHTML = '';
			for(var i = 0; i < data.length; i++) {
				var obj = data[i];
				document.getElementById("navbox").insertAdjacentHTML(
					'beforeend', 
					'<h3 style="padding: 0px; margin: 0px;">' + obj.type + '</h3><B>auteur:</B> <I>' + obj.author + '</I><br><B>gevalideerd:</B> ' + obj.validated + 
					'<br><B>tijd:</B> <I>' + obj.tijd + '</I><br>' + obj.description + '<br><br>'
				);
			}
		});
	document.getElementById("naam").value = '';
	document.getElementById("opmerking").value = '';
}

function closeNav() {
	document.getElementById("mySidenav").style.width = "0";
	document.getElementById("mySidenav").style.paddingLeft = "0px";
	document.getElementById("navbox").innerHTML = '';
}
