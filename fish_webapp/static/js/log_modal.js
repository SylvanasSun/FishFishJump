function bindInfoToLogModal(logs_name, logs_url) {
    $("#hidden_modal_log_names").val(logs_name.join());
    $("#hidden_modal_log_urls").val(logs_url.join());
}

$('#logModal').on('shown.bs.modal', function () {
    var logModalContent = $("#logModalContent");
    var logs_name = $("#hidden_modal_log_names").val().split(',');
    var logs_url = $("#hidden_modal_log_urls").val().split(',');
    for (var i = 0; i < logs_url.length; i++) {
        logModalContent.append($("<a href='" + logs_url[i] + "'>" + logs_name[i] + "</a>"));
    }
});
