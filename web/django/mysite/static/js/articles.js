var isAjaxNow = false;

function getBodyScrollTop() {
    const el = document.scrollingElement || document.documentElement;
    return el.scrollTop
}

window.onscroll = function() {
    if (getBodyScrollTop() < document.getElementById('article_wrap').clientHeight * 0.7) {
        return
    }
    load_more($('#article_wrap').attr('data-last-id'));
};

if (typeof to_bookmarks === "undefined") {
    function to_bookmarks() {
        return false;
    }
}

function load_more(last_id) {
    if (!isAjaxNow) {
        isAjaxNow = true;
        var url = get_url(last_id);
        $.ajax({
            type: 'POST',
            url: url,
            success: function(data) {
                if ('error' in data) {
                    swal(data['error'], {
                        icon: 'error',
                    });
                } else {
                    $("#article_wrap").append(data['articles_htmled']);
                    $('#article_wrap').attr('data-last-id', data['last_id']);
                }
                isAjaxNow = data['last_id'] === 'last';
                if (isAjaxNow) {
                    $('#load-btn').css('display', 'none');
                }
                $(function() {
                    $('[data-action="bookmark"]').click(to_bookmarks);
                });
            }
        });
    }

}

function detect_button(e){
    e = e || window.event;

    if (e.which == null){
        button = (e.button < 2) ? 'left' : ((e.button == 4) ? 'middle' : 'right');
    }
    else{
        button = (e.which < 2) ? 'left' : ((e.which == 2) ? 'middle' : 'right');
    }
    return button;
}

$('.5gnews-card').on('click', function(e) {
   if( detect_button(e) == 'middle' ) {
      e.preventDefault();
      alert("middle button");
   }
});