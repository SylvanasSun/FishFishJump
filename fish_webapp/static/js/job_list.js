function bindJobInfoToModal(job_id, project_name, spider_name) {
    $("#hidden_modal_job_id").val(job_id);
    $("#hidden_modal_project_name").val(project_name);
    $("#hidden_modal_spider_name").val(spider_name);
}

function generatePendingJobList(list) {
    tableBody = $("#pendingJobListDataTableBody");
    for (var p in list) {
        tr = $("<tr></tr>");
        tr.append($("<td>" + p.job_id + "</td>"));
        tr.append($("<td>" + p.project_name + "</td>"));
        tr.append($("<td>" + p.project_version + "</td>"));
        tr.append($("<td>" + p.spider_name + "</td>"));
        tr.append($("<td>" + p.args + "</td>"));
        tr.append($("<td>" + p.priority + "</td>"));
        tr.append($("<td>" + p.creation_time + "</td>"));
        tr.append($("<td><button class='btn btn-primary btn-lg' data-toggle='modal' " +
            "onclick='bindJobInfoToModal(" + p.job_id + "," + p.project_name + "," + p.spider_name + ")' " +
            "data-target='#logModal'>Log</button></td>"));
        tableBody.append(tr);
    }
}

function generateRunningJobList(list) {
    tableBody = $("#runningJobListDataTableBody");
    for (var r in list) {
        tr = $("<tr></tr>");
        tr.append($("<td>" + p.job_id + "</td>"));
        tr.append($("<td>" + p.project_name + "</td>"));
        tr.append($("<td>" + p.project_version + "</td>"));
        tr.append($("<td>" + p.spider_name + "</td>"));
        tr.append($("<td>" + p.args + "</td>"));
        tr.append($("<td>" + p.priority + "</td>"));
        tr.append($("<td>" + p.creation_time + "</td>"));
        tr.append($("<td>" + p.start_time + "</td>"));
        tr.append($("<td><button class='btn btn-primary btn-lg' data-toggle='modal' " +
            "onclick='bindJobInfoToModal(" + p.job_id + "," + p.project_name + "," + p.spider_name + ")' " +
            "data-target='#logModal'>Log</button></td>"));
        tableBody.append(tr);
    }
}

function generateFinishedJobList(list) {
    tableBody = $("#finishedJobListDataTableBody");
    for (var r in list) {
        tr = $("<tr></tr>");
        tr.append($("<td>" + p.job_id + "</td>"));
        tr.append($("<td>" + p.project_name + "</td>"));
        tr.append($("<td>" + p.project_version + "</td>"));
        tr.append($("<td>" + p.spider_name + "</td>"));
        tr.append($("<td>" + p.args + "</td>"));
        tr.append($("<td>" + p.priority + "</td>"));
        tr.append($("<td>" + p.creation_time + "</td>"));
        tr.append($("<td>" + p.start_time + "</td>"));
        tr.append($("<td>" + p.end_time + "</td>"));
        tr.append($("<td><button class='btn btn-primary btn-lg' data-toggle='modal' " +
            "onclick='bindJobInfoToModal(" + p.job_id + "," + p.project_name + "," + p.spider_name + ")' " +
            "data-target='#logModal'>Log</button></td>"));
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

$('#logModal').on('shown.bs.modal', function () {
    $.ajax({
        url: "/supervisor/scrapyd/job/logs",
        type: "GET",
        data: {
            "project_name": $("#hidden_modal_project_name").val(),
            "spider_name": $("#hidden_modal_spider_name").val()
        },
        success: function (data) {
            $("#logmodallabel").text("Job Logs(" + $("#hidden_modal_job_id").val() + ")");
            logModalContent = $("#logModalContent");
            for (var i = 0; i < data.logs_url.length; i++) {
                logModalContent.append($("<a href='" + data.logs_url[i] + "'>" + data.logs_name[i] + "</a>"));
            }
        }
    });
});

$("#pendingJobListDataTable").DataTable();
$("#runningJobListDataTable").DataTable();
$("#finishedJobListDataTable").DataTable();
