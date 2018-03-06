//ready the dom.
$(document).ready(function () {
    var search = $(".search");

    //when the search box is entered
    search.focus(function () {
        //slideDown the results div
        $(".result").slideDown(200);
        //slideDown the loading gif
        $(".gif").slideDown(200);
        //animate the form to the top
        $(".form").animate({
            top: "-190px",
        });
        //fadeOut out the yioop menu
        $(".yioop").fadeOut(500);
        //fadeIn the seearch results
        $(".res li").fadeIn(1000);
        //when the search box is unfocused:
    }).blur(function () {
        //slideUp the results div
        $(".result").slideUp(200);
        //slideUp the loading gif
        $(".gif").slideUp(200);
        //animate the form back to its original position
        $(".form").animate({
            top: "0px",
        });
        //fadeIn the yioop menu
        $(".yioop").fadeIn(1000);
        //fadeOut the search results
        $(".res li").fadeOut(500);
    });

    search.keypress(function (e) {
        if (e.which === 13) {
            value = search.val();
            $("#searching").text("Searching for " + value + "....");
            window.location.href = "/search?keywords=" + value;
        }
    });
});
