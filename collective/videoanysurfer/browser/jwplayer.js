$(document).ready(function(){
  var $yt_links = $("a.videoanysurfer[href*='http://www.youtube.com/watch']");
  $.each($yt_links, function(i) {
	  jwplayer("jwplayer-container").setup(videoanysurfersettings);
  }
});
