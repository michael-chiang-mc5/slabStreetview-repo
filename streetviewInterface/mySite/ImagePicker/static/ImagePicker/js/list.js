
$(document).ready(function() {

  $(".streetviewImage").mousedown(function(e){
     var parentOffset = $(this).parent().offset();
     //or $(this).offset(); if you really just want the current element's offset
     var relX = e.pageX - parentOffset.left;
     var relY = e.pageY - parentOffset.top;
  });

  $(".streetviewImage").mouseup(function(e){
     var parentOffset = $(this).parent().offset();
     //or $(this).offset(); if you really just want the current element's offset
     var relX = e.pageX - parentOffset.left;
     var relY = e.pageY - parentOffset.top;
     alert(relX)
  });


});
