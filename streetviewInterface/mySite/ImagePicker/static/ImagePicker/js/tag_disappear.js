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



// When button is clicked, run search over map
$(document).ready(function() {

  $(".tag_disappear" ).hover(function() {
    $(".tag_disappear" ).css("opacity", "0"); 
  }, function() {
    $(".tag_disappear" ).css("opacity", "0.5");
  });
});
