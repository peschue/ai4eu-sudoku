
var active_cell = null;

function reset() {
  $('.selector').hide()
  $('#status').html('Click on a cell to change.')
}

function reset_cell(value) {
  let cellid = active_cell.attr('id')
  console.log("resetting cell "+cellid)
  active_cell.html('?')
  $.ajax({ type:'PUT', url: 'user_setcell?x='+x+'&y='+y })
}
function set_cell(value) {
  let cellid = active_cell.attr('id')
  let x = cellid.split('_')[0]
  let y = cellid.split('_')[1]
  console.log("setting cell "+cellid+" to "+value)
  active_cell.html(value)
  $.ajax({ type:'PUT', url: 'user_setcell?x='+x+'&y='+y+'&value='+value })
}

async function poll_for_gui_updates() {
  await $.ajax({
    url: 'wait_update?timeout_ms=10000',
    success: function(result) {
      if( result != null ) {
        console.log("got gui update: "+JSON.stringify(result))

        $('#serverstatus').html(result.statusbar);

      }
      // schedule this one immediately
      setTimeout(poll_for_gui_updates, 100);
    }
  })
}

$(document).ready(function() {
  reset()

  $('.cell').click(function(ev) {
    ev.stopPropagation();
    active_cell = $(this);
    let pos = $(this).position();
    let current = $(this).html();
    console.log("click on cell "+current);
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
      reset_cell()
    } else {
      set_cell(current)
    }
    reset()
  })

  setTimeout(poll_for_gui_updates, 1);

  $(document).click(reset)

});
