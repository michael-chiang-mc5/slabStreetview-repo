/*
 * Click the map to set a new location for the Street View camera.
 * helpful information:
 * https://developers.google.com/maps/documentation/javascript/streetview
 */

var usc = {lat: 34.022352, lng: -118.285117};
var search_radius = 49

var map;
var panorama;
var sv

var latitude_val
var longitude_val
var heading_val


function initMap() {
  sv = new google.maps.StreetViewService();

  panorama = new google.maps.StreetViewPanorama(document.getElementById("pano"));

  // Set the initial Street View camera to the center of the map
  sv.getPanorama(
    {location: usc, radius: search_radius}
  );

  // Set up the map.
  map = new google.maps.Map(document.getElementById('map'), {
    center: usc,
    zoom: 16,
    streetViewControl: false
  });

  // Look for a nearby Street View panorama when the map is clicked.
  // getPanoramaByLocation will return the nearest pano when the
  // given radius is 50 meters or less.
  map.addListener('click', function(event) {
    sv.getPanorama({location: event.latLng, radius: search_radius}, processSVData);
    //alert(event.latLng)
  });

  // Detects when panorama changes
  // Sets heading to be orthogonal to street orientation
  // sends data to storePoint
  panorama.addListener('links_changed', function() {
    var links =  panorama.getLinks();

    // an alternative method of getting heading is panorama.getPhotographerPov()
    photographerHeading_val = links[0].heading;


    // TODO: ajax call with latitude_val, longitude_val, heading_val
    $.ajax({
      type        : 'POST', // define the type of HTTP verb we want to use (POST for our form)
      url         : '/ImagePicker/savePoint/', // the url where we want to POST
      data        : {'photographerHeading':photographerHeading_val,
                     'latitude':latitude_val,
                     'longitude':longitude_val,
                     'csrfmiddlewaretoken':csrf_token}, // our data object
      success: function(data, textStatus, jqXHR) {
        alert("sucess!")
      },
      error: function (jqXHR, textStatus, errorThrown) {
        alert("image was not saved")
      }
    });


    panorama.setPov({
        heading: photographerHeading_val + 90,
        pitch: 0,
        zoom: 1
    });
  });

}

function processSVData(data, status) {
  if (status === 'OK') {
    var marker = new google.maps.Marker({
      position: data.location.latLng,
      map: map,
      title: data.location.description
    });

    // set global var so we can package it with heading and send  it to server later
    latitude_val = data.location.latLng.lat()
    longitude_val = data.location.latLng.lng()

    panorama.setPano(data.location.pano);
    panorama.setVisible(true);

    // This shows view if marker is clicked
    /*
    marker.addListener('click', function() {
      var markerPanoID = data.location.pano;
      // Set the Pano to use the passed panoID.
      panorama.setPano(markerPanoID);
      panorama.setPov({
        heading: 270,
        pitch: 0
      });
      panorama.setVisible(true);
    });
    */
  } else {
    console.error('Street View data not found for this location.');
  }
}
