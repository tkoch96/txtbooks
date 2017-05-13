$(function() {
	function processData(deeta) {
		$('#content').html(data);
	}


	$.get(
		'/all_prices',
		function(data) {
			processData(data);
		}
	);
});