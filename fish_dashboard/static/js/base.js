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