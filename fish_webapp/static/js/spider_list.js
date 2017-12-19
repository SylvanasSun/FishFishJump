function generateSpiderList(list) {
    var tableBody = $("#spiderListDataTableBody");
    for (var s in list) {
        var tr = $("<tr></tr>");
        tr.append($("<td>" + s.spider_name + "</td>"));
        tr.append($("<td>" + s.project_name + "</td>"));
        tr.append($("<td>" + s.latest_project_version + "</td>"));
        tr.append($("<td>" + s.pending_job_amount + "</td>"));
        tr.append($("<td>" + s.running_job_amount + "</td>"));
        tr.append($("<td>" + s.finished_job_amount + "</td>"));
        tr.append($("<td><button class='btn btn-primary btn-lg' data-toggle='modal' " +
            "onclick='bindInfoToLogModal(" + s.logs_name + "," + s.logs_url + ")' data-target='#logModal'>" +
            "Log</button></td>"));
        tableBody.append(tr);
    }
}

$.ajax({
    url: "/supervisor/scrapyd/spider/list",
    type: "GET",
    success: function (data) {
        generateSpiderList(data);
    }
});

$("#spiderListDataTable").DataTable();