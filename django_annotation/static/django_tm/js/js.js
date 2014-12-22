$(function() {
    $('textarea#dtm-top-search-input').focus(function () {
	$(this).addClass('absolute');
	$(this).addClass('dtm-top-search-input-focus');
	$(this).css('height','auto');
	$(this).animate({ rows: 5}, 0);
    });
    $('textarea#dtm-top-search-input').blur(function (e) {
	console.log(e.target.id);
	if (e.target.id == 'dtm-top-search-submit'){
            e.cancelBubble = true;
            return false; // return needs to be last
	}
	$(this).animate({ rows: 1}, 0);
	$(this).css('height','34px');
	$(this).removeClass('absolute');
	$(this).removeClass('dtm-top-search-input-focus');
    });
});

$(document).ready(function(){
    $('#dtm-search-result-table').DataTable({
	"dom": '<"#dtm-datatable-top.col-md-7"plf>rt<"bottom"ip><"clear">',	
	"aaSorting": [],
	"pagingType": "simple_numbers",
	stateSave: true,
	"language": {
	    "paginate": {
		"next": "&gt;",
		"previous": "&lt;",
	    },
	    "search": "Filter:",
	}
    });
});