// Center of London by default
var pos = {lat: 51.50986, lng: -0.118092};
var infoWindow;
var map;
function initMap() 
{
	map = new google.maps.Map(document.getElementById('map'), 
			{center: pos, zoom: 16});
	google.maps.event.addListener(map, "rightclick", function(event) 
	{
		pos.lat = event.latLng.lat();
		pos.lng = event.latLng.lng();
		// Set current position by right click
		JobPos("Current position set.");
	});
	infoWindow = new google.maps.InfoWindow({map: map});
	if (navigator.geolocation) 
	{
		// Start geolocation.
		navigator.geolocation.getCurrentPosition(
		function(position) 
		{
			pos = {lat: position.coords.latitude, lng: position.coords.longitude};
			JobPos('You are here.');
		}, 
		function() 
		{
			JobPos('Geolocation failed! Using center of London.');
		});
	} else 
	{
		JobPos('No geolocation support! Using center of London.');
	}
}

var markers = [];
// Clear all markers on the map.
function clearAllMarkers() 
{
	for (var i = 0; i < markers.length; i++) 
	{
		markers[i].setMap(null);
	}
         markers.length = 0;
}

function JobPos(msg)
{
	clearAllMarkers();
	// Use svg red circle for current position
	var geoIcon = 
	{
		path: "M-20,0a20,20 0 1,0 40,0a20,20 0 1,0 -40,0",
		fillColor: '#FF0000',
		fillOpacity: .6,
		anchor: new google.maps.Point(0,0),
		strokeWeight: 0,
		scale: 1 
	};
	infoWindow.setPosition(pos);
	infoWindow.setContent(msg);
	map.setCenter(pos);
	var geoMarker = new google.maps.Marker(
	{
		position: pos,
		map: map,
		title: msg 
	});
	geoMarker.setMap(map);
        markers.push(geoMarker);
	geoMarker.setIcon(geoIcon);
	geoMarker.addListener('click', function() 
	{
		infoWindow.setContent(geoMarker.getTitle());
		infoWindow.open(map, geoMarker);
		infoWindow.setPosition(geoMarker.getPosition());
		map.setCenter(geoMarker.getPosition());
	});

	$.ajax(
	{ 
		type: "POST", url: "/coordinates", contentType: "application/json",
		data: JSON.stringify({location: pos}), dataType: "json",
		success: function(msg) { console.log(msg); },
		error: function(msg) { console.log(msg); }
	}).done(showStops);
}

function displayErr(err)
{
	// In case of error display it in a window
	document.getElementById('stops').innerHTML = err;
}

function showStops(stopS)
{
	if (stopS.Error)
	{
		displayErr(stopS.Error);
		return;
	}
	data = stopS.Data.stopPoints;
	for(var i=0;i<data.length;i++)
	{
		var stopLatLng = new google.maps.LatLng(data[i].lat,data[i].lon);
		var marker = new google.maps.Marker(
		{
			position: stopLatLng,
			map: map,
			title: data[i].commonName
		});
		markers.push(marker);
		marker.setMap(map);
		google.maps.event.addListener(marker, 'click', (function(marker, i) 
		{
			return function() 
			{
				infoWindow.setContent(marker.getTitle());
				infoWindow.open(map, marker);
				infoWindow.setPosition(marker.getPosition());
				console.log(data[i].stopType);    
				$.ajax(
				{ 
					type: "POST", url: "/timetable", contentType: "application/json",
					data: JSON.stringify({stopid: data[i].naptanId}), dataType: "json",
					success: function(msg) { console.log(msg); },
					error: function(msg) { console.log(msg); }
				}).done(showTimetable);

			}
		})(marker, i));
	}
}

function showTimetable(timeTableS)
{
	if (timeTableS.Error)
	{
		displayErr(timeTableS.Error);
		return;
	}
	timeTable = timeTableS.Data;
	if (!timeTable.length)
	{
		displayErr("Sorry, no arrival data available.");
		return;
	}
	// Sort by time arrival
        timeTable.sort((a, b) => (a.timeToStation > b.timeToStation) ? 1 : -1);
	// TODO: move table styles to css
	var htmlTable="<table><caption>"+timeTable[0].stationName+"</caption>";
	htmlTable+="<tr><td style='width: 50px; color: blue;'>Type</td>";
 	htmlTable+="<td style='width: 50px; color: blue; text-align: right;'>Line</td>";
 	htmlTable+="<td style='width: 400px; color: blue; text-align: right;'>Destination</td>";
	htmlTable+="<td style='width: 150px; color: blue; text-align: right;'>Time to station</td>";
	htmlTable+="<td style='width: 200px; color: blue; text-align: right;'>Expected</td></tr>";
	for(var i=0;i<timeTable.length;i++)
	{
		htmlTable+="<tr><td style='width: 50px;'>"+timeTable[i].modeName+"</td>";
		htmlTable+="<td style='width: 50px; text-align: right;'>"+timeTable[i].lineName+"</td>";
		htmlTable+="<td style='width: 400px; text-align: right;'>"+timeTable[i].destinationName+"</td>";
		htmlTable+="<td style='width: 150px; text-align: right;'>"+timeTable[i].timeToStation+"</td>";
		htmlTable+="<td style='width: 200px; text-align: right;'>"+timeTable[i].expectedArrival+"</td></tr>";
	}
	htmlTable+="</table>";
	document.getElementById('stops').innerHTML = htmlTable;
}

