
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
  let x = cellid.split('_')[0]
  let y = cellid.split('_')[1]
  console.log("resetting cell "+cellid)
  active_cell.removeClass('active')
  active_cell.find('.user').html('?')
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
    url: 'wait_update?timeout_ms=5000',
    success: function(result) {
      if( result != null ) {
        //console.log("got gui update: "+JSON.stringify(result))
        console.log("got gui update with statusbar "+result.statusbar)
        $('#serverstatus').html(result.statusbar)
        $('.solution').css('visibility', 'hidden').html('')
        $('.problem').css('visibility', 'hidden').html('')
        for(var f of result.field) {
          //console.log("f "+JSON.stringify(f));
          let sel1 = '#'+f.x+'_'+f.y
          let elm = $(sel1).find('.'+f.cssclass)
          elm.html('&nbsp;'+f.content)
          elm.css('visibility', 'visible')
        }
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
    $('#status').html('Click on a grey digit to set it, click on a green digit to reset it, click outside the field to cancel.')

    active_cell = $(this);
    let pos = $(this).position();
    let current = $(this).attr('id')
    //console.log("click on cell "+current+" with pos "+pos.top+"/"+pos.left);
    $('.selector').css({top:pos.top, left:pos.left});
    $('.selector').show();
    //??? $('.selector .item').removeClass('active');
    //if( current != '?' )
    //  active_cell.find('.user').addClass('active');
  })

  $('.item').click(function() {
    let current = $(this).html();
    //console.log("current = "+current+" active_cell = "+JSON.stringify(active_cell));
    if( active_cell.find('.user').html() == current ) {
      reset_cell()
    } else {
      set_cell(current)
    }
    reset()
  })

  setTimeout(poll_for_gui_updates, 1);

  $(document).click(reset)

  // let server know that we reset
  $.ajax({ type:'PUT', url: 'reset' })
});
