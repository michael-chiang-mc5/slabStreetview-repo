/*
 * Click the map to set a new location for the Street View camera.
 * helpful information:
 * https://developers.google.com/maps/documentation/javascript/streetview
 */

var search_radius = 20

var mapPoint_count = 0
var map;
var panorama;
var sv

var latitude_val
var longitude_val
var heading_val

var start_latLng
var end_latLng
var end_panoID

$(document).ready(function() {
  $('#calculate_route').click(function() {
    routePicker(start_latLng);
  });
});

function initMap() {
  sv = new google.maps.StreetViewService();
  panorama = new google.maps.StreetViewPanorama(document.getElementById("pano"));


  // Set up the map.
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 34.022352, lng: -118.285117},
    zoom: 16,
    streetViewControl: false
  });

  // fill in markers
  for(count = 0; count < initial_mapPoints.length; count++){
    var marker = new google.maps.Marker({
      position: initial_mapPoints[count],
      map: map,
    });
  }


  // detect start/end
  map.addListener('click', function(event) {
    if ( $("#radio_start").is(':checked') ) {
      sv.getPanorama({location: event.latLng, radius: search_radius}, setStartLatLng);
    }
    if ( $("#radio_end").is(':checked') ) {
      sv.getPanorama({location: event.latLng, radius: search_radius}, setEndLatLng);
    }

  });
  function setStartLatLng(data, status) {
    var marker = new google.maps.Marker({
      position: data.location.latLng,
      map: map,
      title: data.location.description
    });
    start_latLng = data.location.latLng
    $("#start_latLng").html("Start: "+start_latLng.lat()+", "+start_latLng.lng())
  }
  function setEndLatLng(data, status) {
    var marker = new google.maps.Marker({
      position: data.location.latLng,
      map: map,
      title: data.location.description
    });
    end_latLng = data.location.latLng
    end_panoID = data.location.pano
    $("#end_latLng").html("End: "+end_latLng.lat()+", "+end_latLng.lng())
  }



  // Detects when panorama changes
  // Sets heading to be orthogonal to street orientation
  // sends data to storePoint
  panorama.addListener('links_changed', function() {
    var links =  panorama.getLinks();
    var photographerHeading_val = panorama.getPhotographerPov().heading;
    var panoID_val = panorama.getPano();


    // links[i] has properties description, heading, pano
    var best_direction = getDegrees(panorama.location.latLng,end_latLng,0)
    var best_i = 0
    min_distance = 9999
    for (var i in links) {
      var angle_diff = angleDistance(links[i].heading,best_direction)
      if ( angle_diff < min_distance ) {
        min_distance = angle_diff
        best_i = i
      }
    }

    var marker = new google.maps.Marker({
      position: panorama.location.latLng,
      map: map,
    });

    mapPoint_count++

    $.ajax({
      type        : 'POST',
      url         : '/ImagePicker/savePoint/',
      data        : {'photographerHeading':photographerHeading_val,
                     'latitude':panorama.location.latLng.lat(),
                     'longitude':panorama.location.latLng.lng(),
                     'panoID':panoID_val,
                     'csrfmiddlewaretoken':csrf_token}, // our data object
      success: function(data, textStatus, jqXHR) {
        if (distanceGPS(panorama.location.latLng,end_latLng) > search_radius ) {
          panorama.setPano(links[best_i].pano);
          panorama.setVisible(true);
        } else {
          $("#distance-traveled").html("Distance: "+ distanceGPS(panorama.location.latLng,start_latLng)+" meters")
          $("#points-saved").html("MapPoints saved: "+ mapPoint_count)
        }



      },
      error: function (jqXHR, textStatus, errorThrown) {
        alert("image was not saved")
      }
    });







  });

}


// returns distance in meters
function distanceGPS(latLng1, latLng2) {
  var lat1 = latLng1.lat()
  var lon1 = latLng1.lng()
  var lat2 = latLng2.lat()
  var lon2 = latLng2.lng()
	var radlat1 = Math.PI * lat1/180
	var radlat2 = Math.PI * lat2/180
	var theta = lon1-lon2
	var radtheta = Math.PI * theta/180
	var dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
	dist = Math.acos(dist)
	dist = dist * 180/Math.PI
	dist = dist * 60 * 1.1515
	dist = dist * 1.609344 * 1000
	return dist
}

function angleDistance(angle1, angle2) {
  ans1 = Math.abs(angle1 - angle2)
  ans2 = Math.abs(360 - ans1)
  return Math.min(ans1,ans2)
}


function getDegrees(latLng1, latLng2, headX) {
    var lat1 = latLng1.lat()
    var lon1 = latLng1.lng()
    var lat2 = latLng2.lat()
    var lon2 = latLng2.lng()
    var dLat = toRad(lat2-lat1);
    var dLon = toRad(lon2-lon1);
    lat1 = toRad(lat1);
    lat2 = toRad(lat2);
    var y = Math.sin(dLon) * Math.cos(lat2);
    var x = Math.cos(lat1)*Math.sin(lat2) -
            Math.sin(lat1)*Math.cos(lat2)*Math.cos(dLon);
    var brng = toDeg(Math.atan2(y, x));
    // enforce domain
    if(brng<0) {
      brng += 360;
    } else if (brng >= 360) {
      brng -= 360;
    }
    return brng - headX;
}
function toRad(degrees){
    return degrees * Math.PI / 180;
}
function toDeg(radians){
    return radians * 180 / Math.PI ;
}


function routePicker(latLng) {
  mapPoint_count = 0
  sv.getPanorama({location: latLng, radius: search_radius}, processSVData);

}

function processSVData(data, status) {
  if (status === 'OK') {

    // set global var so we can package it with heading and send  it to server later
    latitude_val = data.location.latLng.lat()
    longitude_val = data.location.latLng.lng()
    panorama.setPano(data.location.pano);
    panorama.setVisible(true);


  } else {
    console.error('Street View data not found for this location.');
  }
}
