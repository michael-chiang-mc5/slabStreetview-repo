/*
 * Click the map to set a new location for the Street View camera.
 * helpful information:
 * https://developers.google.com/maps/documentation/javascript/streetview
 *
 * DirectionsService provides functionality to calculate routes but GPS coordinates are
 * to coarse to be useful (https://developers.google.com/maps/documentation/javascript/directions#TravelModes)
 * Another option is to use OpenStreetMap but coordinates might not match with google
 *
 */

var search_radius = 20

var map;
var panorama;
var sv

var latitude_val
var longitude_val
var heading_val

var start_latLng


// When button is clicked, run search over map
$(document).ready(function() {
  $('#calculate_route').click(function() {
    bfs(start_latLng);
  });
});

function bfs(latLng) {
  sv.getPanorama({location: latLng, radius: search_radius}, processSVData);
}

// when panorama is set, it updates
// when panorama updates, recursion
function processSVData(data, status) {
  if (status === 'OK') {
    // set global var so we can package it with heading and send  it to server later
    latitude_val = data.location.latLng.lat()
    longitude_val = data.location.latLng.lng()
    panorama.setPano(data.location.pano);
  } else {
    console.error('Street View data not found for this location.');
  }
}





// Initialize map
//   - display in div
//   - fill in markers
//   - add listener to get start point
function initMap() {

  // initialize
  sv = new google.maps.StreetViewService();
  panorama = new google.maps.StreetViewPanorama(document.getElementById("pano"));

  // Set up the map.
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 34.022352, lng: -118.285117},
    zoom: 16,
    streetViewControl: false
  });
  // fill in markers: TODO: too slow
  for(count = 0; count < initial_mapPoints.length; count++){
    if (Math.random() < 0.1) {
      var marker = new google.maps.Marker({
        position: initial_mapPoints[count],
        map: map,
      });
    }
  }

  // listener for start point
  //   - adds marker on map
  //   - sets start point global variable
  map.addListener('click', function(event) {
    sv.getPanorama({location: event.latLng, radius: search_radius}, setStartLatLng);
  });
  function setStartLatLng(data, status) {
    var marker = new google.maps.Marker({
      position: data.location.latLng,
      map: map,
      title: data.location.description
    });
    start_latLng = data.location.latLng // global variable
  }

  // Detects when panorama changes
  //   - sets marker on map (for display only)
  //   - sends POST data to backend
  panorama.addListener('links_changed', function() {
    var photographerHeading_val = panorama.getPhotographerPov().heading;
    var panoID_val = panorama.getPano(); // this is unstable across browser sessions
    var links =  panorama.getLinks(); // links[i].pano gives the pano id of ith link
    // create an array of pano IDs for objects in links
    var links_pano = []
    for (var i = 0; i < links.length; i++) {
      links_pano.push(links[i].pano)
    }
    // mark on map: TODO too slow
    if (Math.random() < 0.1) {
      var marker = new google.maps.Marker({
        position: panorama.location.latLng,
        map: map,
      });
    }


    $.ajax({
      type        : 'POST',
      url         : '/ImagePicker/bfs/',
      data        : {'photographerHeading':photographerHeading_val,
                     'latitude':panorama.location.latLng.lat(),
                     'longitude':panorama.location.latLng.lng(),
                     'panoID':panoID_val,
                     'links':links_pano,
                     'mapPointTag':$("#marker_tag").val(),
                     'csrfmiddlewaretoken':csrf_token}, // our data object
      success: function(data, textStatus, jqXHR) {
        //alert("initial:"+panoID_val+", next:"+data['pano_id']+ ", queue="+data['queue'])
        panorama.setPano(data['pano_id']);
      }, error: function (jqXHR, textStatus, errorThrown) {
        alert("fail")
      }
    });






  });

}