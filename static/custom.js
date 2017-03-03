$(document).ready(function() {
  // Init all tooltips and popovers
  $('[data-toggle="tooltip"]').tooltip();
  $('[data-toggle="popover"]').popover();
  new Clipboard('.clip-button');

  // Share scoreboard button clicked
  $("#share-button").click(function(){
    $('[data-toggle="popover"]').popover('hide');
  });
});
