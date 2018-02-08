function generateProjectList(list) {
    var tableBody = $("#projectListDataTableBody");
    tableBody.children().remove();
    for (var i = 0; i < list.length; i++) {
        var tr = $("<tr></tr>");
        tr.append($("<td>" + list[i].project_name + "</td>"));
        tr.append($("<td>" + list[i].project_versions.join() + "</td>"));
        tr.append($("<td>" + list[i].latest_project_version + "</td>"));
        tr.append($("<td>" + list[i].spider_amount + "</td>"));
        tr.append($("<td>" + list[i].spider_names.join() + "</td>"));
        tr.append($("<td>" + list[i].pending_job_amount + "</td>"));
        tr.append($("<td>" + list[i].running_job_amount + "</td>"));
        tr.append($("<td>" + list[i].finished_job_amount + "</td>"));
        tableBody.append(tr);
    }
}

function ajax_project_list() {
    $.ajax({
        url: "/scrapyd/project/list",
        type: "GET",
        success: function (data) {
            timeout_alert(data[polling_info.failure_message_key]);
            generateProjectList(data);
        },
        error: function (xhr, message, throwable) {
            ajax_error_alert(xhr.status, message);
        }
    });
}

invoke_polling(ajax_project_list);

$("#projectListDataTable").DataTable();
