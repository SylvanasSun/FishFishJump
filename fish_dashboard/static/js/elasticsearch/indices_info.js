function ajax_indices_simple_info() {
    $.ajax({
        url: "/elasticsearch/indices/simple/info",
        type: "GET",
        success: function (data) {
            timeout_alert(data[polling_info.failure_message_key]);
            var tbody = $("#indices_info_tbody");
            tbody.children().remove();
            for (var i = 0; i < data.length; i++) {
                var tr = $("<tr></tr>");
                tr.append($("<th scope='row'>" + (i + 1) + "</th>"));
                tr.append($("<td>" + data[i]['index'] + "</td>"));
                tr.append($("<td></td>").append(generate_health_badge(data[i]['health'])));
                tr.append($("<td>" + data[i]['docs_count'] + "</td>"));
                tr.append($("<td>" + data[i]['docs_deleted'] + "</td>"));
                tr.append($("<td>" + data[i]['pri'] + "</td>"));
                tr.append($("<td>" + data[i]['pri_store_size'] + "</td>"));
                tr.append($("<td>" + data[i]['rep'] + "</td>"));
                tr.append($("<td><span class='badge badge-primary badge-pill'>" + data[i]['status'] + "</span></td>"));
                tr.append($("<td>" + data[i]['store_size'] + "</td>"));
                tr.append($("<td>" + data[i]['uuid'] + "</td>"));
                tr.append($("<td><button class='btn btn-outline-primary' onclick='open_index_stats(\"" + data[i]['index'] + "\")'>Details</button></td>"));
                tbody.append(tr);
            }
        },
        error: function (xhr, message, throwable) {
            ajax_error_alert(xhr.status, message);
        }
    });
}

function generate_health_badge(health) {
    if (health === "green") {
        return $("<span class='badge badge-success badge-pill'>" + health + "</span>");
    } else if (health === "yellow") {
        return $("<span class='badge badge-warning badge-pill'>" + health + "</span>");
    } else if (health === "red") {
        return $("<span class='badge badge-danger badge-pill'>" + health + "</span>");
    } else {
        return $("<span>Not found health status</span>");
    }
}

function handle_indices_stats_modal(data_name, data, first_item_name) {
    var main_name = "indices_stats_%NAME%_content";
    main_name = main_name.replace(/%\w+%/g, function () {
        return data_name;
    });

    for (var key in data) {
        var body_id = main_name + "_" + key + "_body";
        if (key === first_item_name) {
            generate_ul_under_body(key, data, body_id, true);
        } else {
            (function (body_id, key) {
                $("#" + main_name + "_" + key).on("shown.bs.tab", function (e) {
                    generate_ul_under_body(key, data, body_id, true);
                });
            })(body_id, key);
        }
    }
}

function open_index_stats(index) {
    $.ajax({
        url: "/elasticsearch/indices/stats/" + index,
        type: "GET",
        success: function (data) {
            timeout_alert(data[polling_info.failure_message_key]);
            $("#indices_stats_modal_title").text("Indices Stats (" + index + ")");
            var index_data = data['indices'][index];
            handle_indices_stats_modal("primaries", index_data['primaries'], "completion");
            handle_indices_stats_modal("total", index_data['total'], "completion");
            $("#indices_stats_modal").modal("show");
        },
        error: function (xhr, message, throwable) {
            ajax_error_alert(xhr.status, message);
        }
    });
}

invoke_polling(ajax_indices_simple_info);