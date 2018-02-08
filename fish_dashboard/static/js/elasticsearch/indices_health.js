function ajax_indices_health() {
    $.ajax({
        url: "/elasticsearch/cluster/indices/health",
        type: "GET",
        success: function (data) {
            timeout_alert(data[polling_info.failure_message_key]);
            var tbody = $("#elasticsearch_indices_health_tbody");
            tbody.children().remove();
            for (var i = 0; i < data.length; i++) {
                var tr = $("<tr></tr>");
                var count = i + 1;
                tr.append($("<th scope='row'>" + count + "</th>"));
                tr.append($("<td>" + data[i].index + "</td>"));
                var status = data[i].status;
                if (status === "green") {
                    tr.append($("<td><span class='badge badge-pill badge-success'>Green</span></td>"));
                } else if (status === "yellow") {
                    tr.append($("<td><span class='badge badge-pill badge-warning'>Yellow</span></td>"));
                } else if (status === "red") {
                    tr.append($("<td><span class='badge badge-pill badge-danger'>Red</span></td>"));
                } else {
                    tr.append($("<td>Get status info error</td>"))
                }
                tr.append($("<td>" + data[i].number_of_shards + "</td>"));
                tr.append($("<td>" + data[i].number_of_replicas + "</td>"));
                tr.append($("<td>" + data[i].active_primary_shards + "</td>"));
                tr.append($("<td>" + data[i].active_shards + "</td>"));
                tr.append($("<td>" + data[i].relocating_shards + "</td>"));
                tr.append($("<td>" + data[i].initializing_shards + "</td>"));
                tr.append($("<td>" + data[i].unassigned_shards + "</td>"));
                tbody.append(tr);
            }
        },
        error: function (xhr, message, throwable) {
            ajax_error_alert(xhr.status, message);
        }
    });
}

invoke_polling(ajax_indices_health);
