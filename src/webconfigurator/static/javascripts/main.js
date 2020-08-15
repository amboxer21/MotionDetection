$(function() {

    var url = new URL(window.document.location);

    $('a.nav-link.home').click(function() {
        window.location.replace(url.origin);
    });
    $('a.nav-link.logs').click(function() {
        window.location.replace(url.origin+'/logs');
    });
    $('a.nav-link.photos').click(function() {
        window.location.replace(url.origin+'/photos');
    });
    $('a.nav-link.configure').click(function() {
        window.location.replace(url.origin+'/configure');
    });

    $('button.btn.btn-default.delete').click(function() {
        document.getElementsByName('image').forEach(function(e) {
            if(e.checked && (e.id !== '.hidden' || e.id !== 'on')) {
                $.ajax({
                    url: '/delete_selected_photos',
                    data: {image : e.id},
                    type: 'POST',
                    success: function(response) {
                        console.log(response);
                    },
                    error: function(error) {
                        console.log(error);
                    }
                });
            }
        });
    });

    $('div.form-group.logs').on('scroll', function() {
        if($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {

            $.ajax({
                url: '/log_loader',
                type: "GET",
                success: function(response) {
                    document.querySelector('div.scrollbox').innerHTML += response + "<br>";
                }
            });
         }
     });

});
