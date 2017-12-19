function generateProjectList(list) {
    tableBody = $("#projectListDataTableBody");
    for (var p in list) {
        tr = $("<tr></tr>");
        tr.append($("<td>" + p.project_name + "</td>"));
        tr.append($("<td>" + p.project_versions.join() + "</td>"));
        tr.append($("<td>" + p.latest_project_version + "</td>"));
        tr.append($("<td>" + p.spider_amount + "</td>"));
        tr.append($("<td>" + p.spider_names.join() + "</td>"));
        tr.append($("<td>" + p.pending_job_amount + "</td>"));
        tr.append($("<td>" + p.running_job_amount + "</td>"));
        tr.append($("<td>" + p.finished_job_amount + "</td>"));
        tableBody.append(tr);
    }
}

$.ajax({
    url: "/supervisor/scrapyd/project/list",
    type: "GET",
    success: function (data) {
        generateProjectList(data);
    }
});

$("#projectListDataTable").DataTable();
