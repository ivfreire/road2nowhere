
function showLargeImage(imagePath) {
    $('body').append('<div class="modal-overlay"><div class="modal-img"><img src="' + imagePath.replace("small","large") + '" /></div></div>');
}

$('div.image-gallery img').each(function (index) {
    if ($(this).attr('onclick') != null) {                    
        if ($(this).attr('onclick').indexOf("runThis()") == -1) {                        
            $(this).click(function () {
                $(this).attr('onclick');
                var src = $(this).attr("src");
                ShowLargeImage(src);
            });
        }
    }
    else {                    
        $(this).click(function () {                        
            var src = $(this).attr("src");
            showLargeImage(src);
        });
    }
});

$('body').on('click', '.modal-overlay', function () {
    $('.modal-overlay, .modal-img').remove();
});