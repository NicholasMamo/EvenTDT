/*
 * Functions to extract the line-ups from livescore.com.
 */

/**
 * Get the list of home players.
 *
 * @return {Array} The array of players.
 */
function getHomePlayers() {
	jQuery(".visible-inline-xxs").remove();
	players = Array();
	jQuery.each($$(".home .name"), function(index, element) {
		players.push($(element).text());
	});
	return players;
}

/**
 * Get the list of away players.
 * Differently from the home players, the away players are reversed.
 *
 * @return {Array} The array of players.
 */
function getAwayPlayers() {
	jQuery(".visible-inline-xxs").remove();
	players = Array();
	jQuery.each($$(".away .name"), function(index, element) {
		players.push($(element).text());
	});
	return players.reverse();
}

/**
 * Get the home substitutes.
 * The last two values are removed because they are the coach and an empty value.
 *
 * @return {Array} The array of substitutes.
 */
function getHomeSubstitutes() {
	substitutes = Array();
	jQuery.each($$(".ply[data-type='home-player-name']"), function(index, element) {
		substitutes.push($(element).text().trim());
	});
	return substitutes.slice(0, substitutes.length - 2);
}

/**
 * Get the away substitutes.
 * The last two values are removed because they are the coach and an empty value.
 *
 * @return {Array} The array of substitutes.
 */
function getAwaySubstitutes() {
	substitutes = Array();
	jQuery.each($$(".ply[data-type='away-player-name']"), function(index, element) {
		substitutes.push($(element).text().trim());
	});
	return substitutes.slice(0, substitutes.length - 2);
}
