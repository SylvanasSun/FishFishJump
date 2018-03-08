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
        // $(".res li").fadeIn(1000);
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
            var value = search.val();
            $("#searching").text("Searching for " + value + "....");
            window.location.href = "/search?keywords=" + value;
        }
    });

    var namespace = "/suggest";
    var addr = location.protocol + "//" + document.domain + ":" + location.port + namespace;
    var socket = io.connect(addr);

    socket.on("render_suggest_list", function (pages_info) {
        pages_info = JSON.parse(pages_info.data);
        var suggest_list = $("#suggest_list");
        suggest_list.children().remove();

        for (var i = 0; i < pages_info.length; i++) {
            var info = pages_info[i];
            var ul = $("<ul class='res clearfix'></ul>");
            var li = $("<li></li>");
            li.append($("<a href='" + info.url + "'><h3>" + info.title + "</h3></a>"));
            li.append($("<p>" + info.description + "</p>"));
            ul.append(li);
            suggest_list.append(ul);
        }

        $("#searching").text("Recommended Result...");
        // show suggest list
        $(".res li").fadeIn(1000);
    });

    search.bind("input", function (e) {
        var value = search.val();
        if (value.length > 0) {
            socket.emit("suggest_result", {data: value});
        } else {
            $(".res li").fadeOut(1000);
        }
    });
});
