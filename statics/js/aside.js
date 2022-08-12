function openBar() {
    toolbar.hasClass("open") || (toolbar.addClass("open")
        ,$("#btn_aside_swich").css({
            "display": "none"
        })
        )
}
function closeBar() {
        toolbar.removeClass("open")
        ,$("#btn_aside_swich").css({
            "display": "block"
        })
}

var toolbar = $(".global_toolbar");
$(function() {

        // $("body").click(function(t) {
        //     toolbar.hasClass("open") && closeBar()
        // }),
        $("#div_body").mouseover(function(t) {
            closeBar()
        }),
        $(".div_body").mouseover(function(t) {
            closeBar()
        }),
        
        $("#btn_aside_swich").click(function(t) {
            t.stopPropagation();
            var e = $(this).attr("data-id"), i = $("." + e);
            $(this).hasClass("current") ? $(this).removeClass("current") : $(this).addClass("current").removeClass("current"),
                i.hasClass("open") ? closeBar() : openBar()
        })

});
