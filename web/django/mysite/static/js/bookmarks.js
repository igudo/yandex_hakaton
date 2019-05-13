var isBookmarkNow = false;

function get_bookmarks_url(type, pk) {
    return "/bookmarks/" + type + "/" + pk + "/";
}

function to_bookmarks()
{
    if (!isBookmarkNow) {
        isBookmarkNow = true;
        var current = $(this);
        var type = current.data('type');
        var pk = current.data('id');
        var action = current.data('action');
        var url = get_bookmarks_url(type, pk);
        $.ajax({
            url : url,
            type : 'POST',
            data : { 'obj' : pk },

            success : function (json) {
                current.find("[data-count='" + action + "']").text(json.count);
                current.children('i').toggleClass('active');
                if (current.children('i').hasClass('active')) {
                    current.attr('title', 'Убрать из избранного');
                    swal('Добавлено в избранное', {
                        icon: 'success',
                    });
                } else {
                    current.attr('title', 'Добавить в избранное');
                    swal('Убрано из избранного', {
                        icon: 'success',
                    });
                }
                isBookmarkNow = false;

            }
        });
    }

    return false;
}

// Подключение обработчика
$(function() {
    $('[data-action="bookmark"]').click(to_bookmarks);
});