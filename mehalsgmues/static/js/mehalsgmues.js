$(function(){
    $.ajax({
        url: URL_ajax_notification
    }).done(function (data) {
        $('sup.notify').removeClass().addClass(['notify', 'notify-' + data]).text(data)
    });
})