function cancelJob(project_name, job_id) {
    $.ajax({
        url: "/supervisor/scrapyd/job/cancel",
        type: "POST",
        data: {
            "project_name": project_name,
            "job_id": job_id
        }
    });
}

function generatePendingJobList(list) {
    var tableBody = $("#pendingJobListDataTableBody");
    for (var p in list) {
        var tr = $("<tr></tr>");
        tr.append($("<td>" + p.job_id + "</td>"));
        tr.append($("<td>" + p.project_name + "</td>"));
        tr.append($("<td>" + p.project_version + "</td>"));
        tr.append($("<td>" + p.spider_name + "</td>"));
        tr.append($("<td>" + p.args + "</td>"));
        tr.append($("<td>" + p.priority + "</td>"));
        tr.append($("<td>" + p.creation_time + "</td>"));
        tr.append($("<td><button class='btn btn-primary btn-lg' data-toggle='modal' " +
            "onclick='bindInfoToLogModal(" + p.logs_name + "," + p.logs_url + ")' data-target='#logModal'>" +
            "Log</button></td>"));
        tr.append($("<td><button type='button' onclick='cancelJob(" + p.project_name + "," + p.job_id + ")' " +
            "class='btn btn-danger'>Cancel</button></td>"));
        tableBody.append(tr);
    }
}

function generateRunningJobList(list) {
    var tableBody = $("#runningJobListDataTableBody");
    for (var r in list) {
        var tr = $("<tr></tr>");
        tr.append($("<td>" + r.job_id + "</td>"));
        tr.append($("<td>" + r.project_name + "</td>"));
        tr.append($("<td>" + r.project_version + "</td>"));
        tr.append($("<td>" + r.spider_name + "</td>"));
        tr.append($("<td>" + r.args + "</td>"));
        tr.append($("<td>" + r.priority + "</td>"));
        tr.append($("<td>" + r.creation_time + "</td>"));
        tr.append($("<td>" + r.start_time + "</td>"));
        tr.append($("<td><button class='btn btn-primary btn-lg' data-toggle='modal' " +
            "onclick='bindInfoToLogModal(" + r.logs_name + "," + r.logs_url + ")' data-target='#logModal'>" +
            "Log</button></td>"));
        tr.append($("<td><button type='button' onclick='cancelJob(" + r.project_name + "," + r.job_id + ")' " +
            "class='btn btn-danger'>Cancel</button></td>"));
        tableBody.append(tr);
    }
}

function generateFinishedJobList(list) {
    var tableBody = $("#finishedJobListDataTableBody");
    for (var r in list) {
        var tr = $("<tr></tr>");
        tr.append($("<td>" + r.job_id + "</td>"));
        tr.append($("<td>" + r.project_name + "</td>"));
        tr.append($("<td>" + r.project_version + "</td>"));
        tr.append($("<td>" + r.spider_name + "</td>"));
        tr.append($("<td>" + r.args + "</td>"));
        tr.append($("<td>" + r.priority + "</td>"));
        tr.append($("<td>" + r.creation_time + "</td>"));
        tr.append($("<td>" + r.start_time + "</td>"));
        tr.append($("<td>" + r.end_time + "</td>"));
        tr.append($("<td><button class='btn btn-primary btn-lg' data-toggle='modal' " +
            "onclick='bindInfoToLogModal(" + r.logs_name + "," + r.logs_url + ")' data-target='#logModal'>" +
            "Log</button></td>"));
        tr.append($("<td><button type='button' onclick='cancelJob(" + r.project_name + "," + r.job_id + ")' " +
            "class='btn btn-danger'>Cancel</button></td>"));
        tableBody.append(tr);
    }
}

$.ajax({
    url: "/supervisor/scrapyd/job/list",
    type: "GET",
    success: function (data) {
        generatePendingJobList(data.pending);
        generateRunningJobList(data.running);
        generateFinishedJobList(data.finished);
    }
});


$("#pendingJobListDataTable").DataTable();
$("#runningJobListDataTable").DataTable();
$("#finishedJobListDataTable").DataTable();
