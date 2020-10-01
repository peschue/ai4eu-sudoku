
var active_cell = null;

function reset() {
  $('.selector').hide()
  $('#status').html('Click on a cell to change.')
}

$(document).ready(function() {
  reset()

  $('.cell').click(function(ev) {
    ev.stopPropagation();
    active_cell = $(this);
    let pos = $(this).position();
    let current = $(this).html();
    $('.selector').css({top:pos.top, left:pos.left});
    $('.selector').show();
    $('.selector .item').removeClass('active');
    if( current != '?' )
      $('#'+current).addClass('active');
    $('#status').html('Click on a grey digit to set it, click on a green digit to reset it, click outside the field to cancel.')
  })

  $('.item').click(function() {
    let current = $(this).html();
    if( $(this).hasClass('active') ) {
      // deactivate
      active_cell.html('?');
    } else {
      // activate
      active_cell.html(current);
    }
    reset()
  })

  $(document).click(reset)

});
