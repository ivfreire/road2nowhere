
$("div.post div.title").on("click", function() {
    $(this).parent().find('.body').slideToggle();
});