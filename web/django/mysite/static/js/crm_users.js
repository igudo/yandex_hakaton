
function getBodyScrollTop() {
    const el = document.scrollingElement || document.documentElement;
    return el.scrollTop
}

window.onscroll = function() {
    if (getBodyScrollTop() < document.getElementById('users').clientHeight * 0.7) {
        return
    }
    load_more($('#users').attr('data-last-id'));
};


function load_more(last_id) {
    if (!isAjaxNow) {
        isAjaxNow = true;
        var url = get_users_url(last_id);
        $.ajax({
            type: 'POST',
            url: url,
            success: function(data) {
                if ('error' in data) {
                    swal(data['error'], {
                        icon: 'error',
                    });
                } else {
                    $("#users").append(data['users_htmled']);
                    $('#users').attr('data-last-id', data['last_id']);
                }
                isAjaxNow = data['last_id'] === 'last';
                if (isAjaxNow) {
                    $('#load-btn').css('display', 'none');
                }
            }
        });
    }

}