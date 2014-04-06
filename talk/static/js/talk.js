(function($) {

    $('textarea').autosize();

    $('.togglesettings').on('click', function(e) {
        e.preventDefault();
        $('#settings').toggle();
    });

    $('#settings').on('change', function(e) {
        var input = $(e.target);
        var form = input.parents('form');

        $.post(form.attr('action'), form.serialize(), function(data) {
            if (data['status'] == 'ok') {
                input.parent().addClass('saved');
                setTimeout(function() {
                    input.parent().removeClass('saved');
                }, 500);
            }
        });
    });

    $('#threads').on('click', '.paginator a', function(e) {
        e.preventDefault();
        var a = $(e.target);
        var url = a.parents('.paginator').data('url');
        var query = a.attr('href');

        $.get(url + query, function(data) {
            $('#threads').html(data);
        });
    });

    $('.threadsearch').on('submit', function(e) {
        e.preventDefault();
        var form = $(e.target);
        var url = form.attr('action');

        $.get(url + '?' + form.serialize(), function(data) {
            $('#threads').html(data);
        });
    });

    $('.newmessage').on('submit', function(e) {
        e.preventDefault();
        var form = $(e.target);

        $.post(form.attr('action'), form.serialize(), function(data) {
            $('#messages').append(data);
            form.trigger('reset');
        });
    });

    var messages = $('#messages');
    if (messages.length !== 0) {
        setInterval(function() {
            messages.find('.new').remove();

            $.get(window.location, function(data) {
                messages.append(data);
                messages.find('.userStates').remove();

                for (var user in userStates) {
                    var userIndicators = $(user);
                    userIndicators.removeClass('inchat idle away');
                    userIndicators.addClass(userStates[user]);
                    userIndicators.attr('title', states[userStates[user]]);;
                }
            });
        }, 10000);
    }

})(jQuery);
