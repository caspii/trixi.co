$(document).ready(function() {
  // Init all tooltips and popovers
  $('[data-toggle="tooltip"]').tooltip();
  $('[data-toggle="popover"]').popover();
  new Clipboard('.clip-button');

  $(".person-button").click(function(){
        var button = $(this);
        var field = '#person_count'
        var old_value = parseInt($(field).val())
        if (button.text() == '+') {
          new_value = old_value + 1
          if (new_value <=10) {
            $(field).val(new_value)
          }
        } else {
          new_value = old_value - 1
          if (new_value >=1) {
            $(field).val(new_value)
          }
        }
    });

});
