function bindInfoToLogModal(project_name, spider_name) {
    $("#logsInfoModalHiddenProjectName").val(project_name);
    $("#logsInfoModalHiddenSpiderName").val(spider_name);
}

$('#logModal').on('shown.bs.modal', function () {
    var projectName = $("#logsInfoModalHiddenProjectName").val();
    var spiderName = $("#logsInfoModalHiddenSpiderName").val();
    $("#logsInfoModalTitle").text("Logs Info(" + projectName + "-" + spiderName + ")");
    $.ajax({
        url: "/supervisor/scrapyd/job/logs",
        type: "GET",
        data: {
            "project_name": projectName,
            "spider_name": spiderName
        },
        success: function (data) {
            var logsInfoModalBody = $("#logsInfoModalBody");
            var logsName = data.logs_name;
            var logsUrl = data.logs_url;
            var logsInfoTable = $("<table class='table table-bordered' " +
                "id='logsInfoTable' width='100%' cellspacing='0'></table>");
            var logsInfoTableHead = $("<thead><tr><th>Logs File Name</th><th>Logs Url</th></tr></thead>");
            var logsInfoTableBody = $("<tbody></tbody>");
            logsInfoTable.append(logsInfoTableHead);
            logsInfoTable.append(logsInfoTableBody);

            for (var i = 0; i < logsName.length; i++) {
                var tr = $("<tr></tr>");
                tr.append($("<td>" + logsName[i] + "</td>"));
                tr.append($("<td><a href='" + logsUrl[i] + "'>Link</a></td>"));
                logsInfoTableBody.append(tr);
            }
            logsInfoModalBody.append(logsInfoTable);
            $("#logsinfoTable").DataTable();
        }
    });
});
