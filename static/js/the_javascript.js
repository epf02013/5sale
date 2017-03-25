$("#menu").on("click",function() {
		$(this).toggleClass("selected");
});

$(window).resize(function() {
	$(".nav-spacer").height($(".navbar-header").height());
	$(".category").height($(".category").width());
});
$(document).ready(function(){
	$(".nav-spacer").height($(".navbar-header").height());
	$(".category").height($(".category").width());
});

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
