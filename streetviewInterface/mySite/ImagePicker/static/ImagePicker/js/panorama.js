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
var panoramaOptions = {
    position: langlongObj,
    visible: true
};

function initMap() {
  sv = new google.maps.StreetViewService();

  panorama = new google.maps.StreetViewPanorama(document.getElementById("pano"), panoramaOptions);

  // Set the initial Street View camera to the center of the map
  sv.getPanorama(
    {location: usc, radius: search_radius},
    processSVData
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

  // Set heading to be orthogonal to street orientation
  panorama.addListener('links_changed', function() {
    var links =  panorama.getLinks();
    //alert(links[0].heading) # this is the heading of the car
    panorama.setPov({
        heading: links[0].heading + 90,
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



    panorama.setPano(data.location.pano);
    panorama.setPov({
      heading: 270,
      pitch: 0
    });
    panorama.setVisible(true);

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
  } else {
    console.error('Street View data not found for this location.');
  }
}
