var global_panorama;

$(document).ready(function() {

  $('.picker-button').click(function(){

    /*
    alert(    $( "#position-cell" ).html() );
    alert(    $( "#heading-cell" ).html()  );
    alert(    $( "#pitch-cell" ).html()    );
    */

    var position = $( "#position-cell" ).html()
    position = position.replace('(', '');
    position = position.replace(')', '');
    var position_array = position.split(',');

    var latitude = position_array[0]
    var longitude = position_array[1]
    var heading = $( "#heading-cell" ).html()
    var pitch = $( "#pitch-cell" ).html()

    var url_saveImage = '/ImagePicker/save_image/' + latitude + '/' + longitude + '/' + heading + '/' + pitch + '/';

    url_saveImage = url_saveImage.replace(' ', '');



    $.ajax({
      type: "GET",
      url: url_saveImage,
      cache: false,
      success: function(data){
        alert('saved')
      }
    });

  });

});
