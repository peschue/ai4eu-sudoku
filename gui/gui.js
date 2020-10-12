
var active_cell = null;

function hide_solution() {
  $('span.solution').css('visibility', 'hidden');
  $('span.solution').html('');
}

function reset() {
  $('.selector').hide()
  $('#status').html('Click on a cell to change.')
  hide_solution()
}

function reset_cell() {
  let cellid = active_cell.attr('id')
  console.log("resetting cell "+cellid)
  active_cell.removeClass('active')
  active_cell.find('user').html('?')
  hide_solution()
  $.ajax({ type:'PUT', url: 'user_setcell?x='+x+'&y='+y })
}
function set_cell(value) {
  let cellid = active_cell.attr('id')
  let x = cellid.split('_')[0]
  let y = cellid.split('_')[1]
  console.log("setting cell "+cellid+" to "+value)
  active_cell.find('.user').html(value)
  active_cell.addClass('active')
  hide_solution()
  $.ajax({ type:'PUT', url: 'user_setcell?x='+x+'&y='+y+'&value='+value })
}

async function poll_for_gui_updates() {
  await $.ajax({
    url: 'wait_update?timeout_ms=1000',
    success: function(result) {
      if( result != null ) {
        console.log("got gui update: "+JSON.stringify(result))
        $('#serverstatus').html(result.statusbar)
        for(var f of result.field) {
          //console.log("f "+JSON.stringify(f));
          let sel1 = '#'+f.x+'_'+f.y;
          //console.log("sel1 "+sel1+" "+JSON.stringify($(sel1).find('.'+f.cssclass)));
          $(sel1).find('.'+f.cssclass).html('&nbsp;=>&nbsp;'+f.content);
        }
        $('.solution').css('visibility', 'visible');
        active_cell.find('.user').html(value)
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
    let current = $(this).attr('id')
    console.log("click on cell "+current);
    $('.selector').css({top:pos.top, left:pos.left});
    $('.selector').show();
    //??? $('.selector .item').removeClass('active');
    //if( current != '?' )
    //  active_cell.find('.user').addClass('active');
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
