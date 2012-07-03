$(document).ready(function(){
    var $yt_links = $("a.videoanysurfer[href*='http://www.youtube.com/watch']");
    $.each($yt_links, function(i) {
        var $holder = $('<span />');
        $(this).parent().replaceWith($holder);
        // Find the captions file if it exists
        var $mycaptions = $(this).siblings('.captions');
        // Work out if we have captions or not
        var captionsf = $($mycaptions).length > 0 ? $($mycaptions).attr('href') : null;
        // Ensure that we extract the last part of the youtube link (the video id)
        // and pass it to the player() method
        var link = $(this).attr('href').split("=")[1];
        // Initialise the player
        $holder.player({
            id:'yt'+i,
            media:link,
            captions:captionsf,
            flashHeight:$holder.parent().height() - 30
        });
    });
});