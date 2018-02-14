function logout() {
    $.ajax({
        url: "/user/logout",
        type: "POST"
    });
}

var polling_info;

function ajax_polling_info() {
    $.ajax({
        url: "/polling/info",
        async: false,
        type: "GET",
        success: function (data) {
            polling_info = data;
        }
    });
}

ajax_polling_info();

function not_undefined(vars) {
    if (Array.isArray(vars)) {
        for (var i = 0; i < vars.length; i++) {
            if (typeof(vars[i]) === "undefined" || vars[i] === null || vars[i] === "")
                return false;
        }
        return true;
    }
    return typeof(vars) !== "undefined" && vars !== null && vars !== "";
}

function invoke_polling(func, func_args) {
    if (polling_info.polling_interval > 0) {
        window.setInterval(function () {
            if (not_undefined(func_args) && Array.isArray(func_args)) {
                func.apply(this, func_args);
            } else {
                func();
            }
        }, polling_info.polling_interval * 1000);
    } else {
        // Get polling info fail and adopt non-polling mode
        if (not_undefined(func_args) && Array.isArray(func_args)) {
            func.apply(this, func_args);
        } else {
            func();
        }
    }
}

function timeout_alert(message) {
    if (not_undefined(message)) {
        swal("Oops!", message, "error");
    }
}

function ajax_error_alert(status_code, message) {
    swal("Oops!", "Ajax request happened error, status code: " + status_code + " message: " + message, "error");
}

function byte_to_gb(bytes_num, fixed) {
    return (bytes_num / 1024 / 1024 / 1024).toFixed(fixed);
}

function byte_to_mb(bytes_num, fixed) {
    return (bytes_num / 1024 / 1024).toFixed(fixed);
}

function get_tag_by_id(id) {
    var tag = null;
    if (id.charAt(0) === "#") {
        tag = $(id);
    } else {
        tag = $("#" + id);
    }

    return tag;
}

function generate_ul(key, data) {
    var ul = $("<ul class='list-group list-group-flush'></ul>");
    var map = data[key];
    for (var k in map) {
        var li = $("<li class='list-group-item'><h5>" + k + "</h5></li>");
        li.append($("<span class='badge badge-primary badge-pill'>" + map[k] + "</span>"));
        ul.append(li);
    }
    return ul;
}

function generate_ul_under_body(key, data, body_id, clean_children) {
    var body = get_tag_by_id(body_id);

    if (clean_children) {
        body.children().remove();
    }

    body.append(generate_ul(key, data));
}