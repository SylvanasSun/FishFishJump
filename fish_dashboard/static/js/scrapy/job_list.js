function cancelJob(project_name, job_id) {
    $.ajax({
        url: "/scrapyd/job/cancel",
        type: "POST",
        data: {
            "project_name": project_name,
            "job_id": job_id
        }
    });
}

function generatePendingJobList(list) {
    var tableBody = $("#pendingJobListDataTableBody");
    for (var i = 0; i < list.length; i++) {
        var tr = $("<tr></tr>");
        tr.append($("<td>" + list[i].job_id + "</td>"));
        tr.append($("<td>" + list[i].project_name + "</td>"));
        tr.append($("<td>" + list[i].project_version + "</td>"));
        tr.append($("<td>" + list[i].spider_name + "</td>"));
        tr.append($("<td>" + list[i].args + "</td>"));
        tr.append($("<td>" + list[i].priority + "</td>"));
        tr.append($("<td>" + list[i].creation_time + "</td>"));
        tr.append($("<td><button class='btn btn-primary btn-lg' data-toggle='modal' " +
            "onclick='bindInfoToLogModal(\"" + list[i].project_name + "\",\"" + list[i].spider_name + "\")' " +
            "data-target='#logModal'>" + "Log</button></td>"));
        tr.append($("<td><button type='button' onclick='cancelJob(\"" + list[i].project_name + "\"" +
            ",\"" + list[i].job_id + "\")' class='btn btn-danger'>Cancel</button></td>"));
        tableBody.append(tr);
    }
}

function generateRunningJobList(list) {
    var tableBody = $("#runningJobListDataTableBody");
    for (var i = 0; i < list.length; i++) {
        var tr = $("<tr></tr>");
        tr.append($("<td>" + list[i].job_id + "</td>"));
        tr.append($("<td>" + list[i].project_name + "</td>"));
        tr.append($("<td>" + list[i].project_version + "</td>"));
        tr.append($("<td>" + list[i].spider_name + "</td>"));
        tr.append($("<td>" + list[i].args + "</td>"));
        tr.append($("<td>" + list[i].priority + "</td>"));
        tr.append($("<td>" + list[i].creation_time + "</td>"));
        tr.append($("<td>" + list[i].start_time + "</td>"));
        tr.append($("<td><button class='btn btn-primary btn-lg' data-toggle='modal' " +
            "onclick='bindInfoToLogModal(\"" + list[i].project_name + "\",\"" + list[i].spider_name + "\")' " +
            "data-target='#logModal'>" + "Log</button></td>"));
        tr.append($("<td><button type='button' onclick='cancelJob(\"" + list[i].project_name + "\"" +
            ",\"" + list[i].job_id + "\")' class='btn btn-danger'>Cancel</button></td>"));
        tableBody.append(tr);
    }
}

function generateFinishedJobList(list) {
    var tableBody = $("#finishedJobListDataTableBody");
    for (var i = 0; i < list.length; i++) {
        var tr = $("<tr></tr>");
        tr.append($("<td>" + list[i].job_id + "</td>"));
        tr.append($("<td>" + list[i].project_name + "</td>"));
        tr.append($("<td>" + list[i].project_version + "</td>"));
        tr.append($("<td>" + list[i].spider_name + "</td>"));
        tr.append($("<td>" + list[i].args + "</td>"));
        tr.append($("<td>" + list[i].priority + "</td>"));
        tr.append($("<td>" + list[i].creation_time + "</td>"));
        tr.append($("<td>" + list[i].start_time + "</td>"));
        tr.append($("<td>" + list[i].end_time + "</td>"));
        tr.append($("<td><button class='btn btn-primary btn-lg' data-toggle='modal' " +
            "onclick='bindInfoToLogModal(\"" + list[i].project_name + "\",\"" + list[i].spider_name + "\")' " +
            "data-target='#logModal'>" + "Log</button></td>"));
        tr.append($("<td><button type='button' onclick='cancelJob(\"" + list[i].project_name + "\"" +
            ",\"" + list[i].job_id + "\")' class='btn btn-danger'>Cancel</button></td>"));
        tableBody.append(tr);
    }
}

$.ajax({
    url: "/scrapyd/job/list",
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
