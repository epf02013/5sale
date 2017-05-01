$("#menu").on("click",function() {
		$(this).toggleClass("selected");
});
$(".list-div").on("click", function(e){
    $(location).attr('href', $(this).data("link"));
  });
$(window).resize(function() {
	$(".nav-spacer").height($(".navbar-header").height());
	$(".category").height($(".category").width());
});
$(document).ready(function(){
	$(".nav-spacer").height($(".navbar-header").height());
	$(".category").height($(".category").width());
});

function display_user(e,user_id) {
	e.stopPropagation();
	console.log("pop");
	$(location).attr('href', '/user/'+user_id);
}
function flag_review(review_id) {
	$.post("/reviews/"+review_id,
            {reason:"flag"},
            function(data, status){
              console.log("flagged");
              alert("Review Flagged");
    });
}
function remove_review(review_id) {
	$.post("/reviews/"+review_id,
            {reason:"remove"},
            function(data, status){
            	$("#review_"+review_id).remove();
    });
}
function remove_offer(offer_id) {
	$.post("/offers/"+offer_id,
            {reason:"remove"},
            function(data, status){
            	$("#offer_"+offer_id).remove();
    });
}
function clear_notifications() {
	$.post("/clear_notifications",
            {reason:"remove"},
            function(data, status){
            	$("#offer_"+offer_id).remove();
    });
}



// var dragging=false;
// var col=-1;
// var start_row=-1;
// var end_row=-1;
// $('.main-td').on('click', function(){
// 	$(this).addClass('highlighted');

// });


// $('.main-td').on('mousedown', function(){
// 	$(this).addClass('highlighted');
// 	dragging=true;
// 	col=$(this).data('col');
// 	start_row=$(this).data('row');
// 	end_row=$(this).data('row');
// 	console.log("POP"+col);


// });
// $(window).on('mouseup', function(){
// 	// $(this).addClass('highlighted');
// 	create_event();
// 	dragging=false;

// });
// $('.main-td').on('mouseover', function(){
// 	if (dragging){
// 		if($(this).data('col')==col) {
// 			if ($(this).data('row')>=start_row) {
// 				end_row=$(this).data('row');
// 				$('.main-td').filter(function(){
// 					return $(this).data('col')==col && $(this).data('row')>start_row &&$(this).data('row')<=end_row;
// 				}).addClass('highlighted');
// 				$('.main-td').filter(function(){
// 					return $(this).data('col')==col && $(this).data('row')>start_row &&$(this).data('row')>end_row;
// 				}).removeClass('highlighted');
				
// 			}
// 		}
// 	}

// });
