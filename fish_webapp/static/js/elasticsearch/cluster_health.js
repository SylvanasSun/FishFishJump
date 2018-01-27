function handle_timed_out(timed_out_tag, data_timed_out) {
    if (!data_timed_out) {
        timed_out_tag.text("No timed out");
        timed_out_tag.append($("<span class='badge badge-pill badge-success'>No timed out</span>"));
    } else if (data_timed_out) {
        timed_out_tag.text("Timed out");
        timed_out_tag.append($("<span class='badge badge-pill badge-danger'>Timed out</span>"));
    }
}

function handle_cluster_status(status_tag, status) {
    if (status === "green") {
        status_tag.text("Status is green (No Fault)");
        status_tag.append($("<span class='badge badge-pill badge-success'>Green</span>"));
    } else if (status === "yellow") {
        status_tag.text("Status is yellow (Replicate Shard Fault)");
        status_tag.append($("<span class='badge badge-pill badge-warning'>Yellow</span>"));
    } else if (status === "red") {
        status_tag.text("Status is red (Main Shard Fault)");
        status_tag.append($("<span class='badge badge-pill badge-danger'>Red</span>"));
    } else {
        status_tag.text("Get status info error");
    }
}

$.ajax({
    url: "/supervisor/elasticsearch/cluster/health/",
    type: "GET",
    success: function (data) {
        $("#cluster_name").text("Cluster Name: " + data.cluster_name);
        var status = data.status;
        var status_tag = $("#status");
        handle_cluster_status(status_tag, status);
        handle_timed_out($("#timed_out", data.timed_out));
        $("#number_of_nodes").children("span").text(data.number_of_nodes);
        $("#number_of_data_nodes").children("span").text(data.number_of_data_nodes);
        $("#number_of_pending_task").children("span").text(data.number_of_pending_tasks);
        $("#number_of_in_flight_fetch").children("span").text(data.number_of_in_flight_fetch);
        $("#task_max_waiting_in_queue_millis").children("span").text(data.task_max_waiting_in_queue_millis);
        $("#active_primary_shards").children("span").text(data.active_primary_shards);
        $("#active_shards").children("span").text(data.active_shards);
        $("#relocating_shards").children("span").text(data.relocating_shards);
        $("#initializing_shards").children("span").text(data.initializing_shards);
        $("#unassigned_shards").children("span").text(data.unassigned_shards);
        $("#delayed_unassigned_shards").children("span").text(data.delayed_unassigned_shards);
        $("#active_shards_percentage").text(data.active_shards_percent_as_number + "%");
    }
});

$.ajax({
    url: "/supervisor/elasticsearch/auto/transfer/status",
    type: "GET",
    success: function (data) {
        var is_auto_transfer = data.is_auto_transfer;
        var transfer_data_card_body = $("#transfer_data_card_body");
        var transfer_data_card_text = $("#transfer_data_card_text");
        if (!is_auto_transfer) {
            var manual_transfer_button = $("<button type='button' data-toggle='modal' " +
                "data-target='#progressBarModal'  class='btn btn-outline-primary'>" +
                "<i class='fa fa-magic mr-1'></i>Manual Transfer</button>");
            var auto_transfer_button = $("<button type='button' class='btn btn-outline-info'>" +
                "<i class='fa fa-magic mr-1'></i>Enable Auto Transfer</button>");
            var row = $("<div class='row'></div>");
            var left_col = $("<div class='col-6'></div>");
            var right_col = $("<div class='col-6'></div>");
            row.append(left_col);
            row.append(right_col);
            left_col.append(manual_transfer_button);
            right_col.append(auto_transfer_button);
            transfer_data_card_body.append(row);
            transfer_data_card_text.text("The current status is non-automatic, " +
                "you can choose means for transfer data from MongoDB into the Elasticsearch.");
        } else {
            transfer_data_card_text.text("The current status is automatically transmitted data " +
                "with synchronized from MongoDB.");
            transfer_data_card_body.append($("<button type='button' class='btn btn-outline-danger'>" +
                "<i class='fa fa-magic mr-1'></i>Cancel</button>"));
        }
    }
});