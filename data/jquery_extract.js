// line-ups
jQuery(".visible-inline-xxs").remove();
jQuery.each($$(".name"), function(index, element) {
	console.log($(element).text());
})

// home subs
jQuery.each($$(".ply[data-type='home-player-name']"), function(index, element) {
	console.log($(element).text().trim());
})

// away subs
jQuery.each($$(".ply[data-type='away-player-name']"), function(index, element) {
	console.log($(element).text().trim());
})
