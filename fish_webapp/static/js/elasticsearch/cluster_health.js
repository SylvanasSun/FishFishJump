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

function enable_transfer() {
    var host = $("#mongo_host").val();
    var port = $("#mongo_port").val();
    var db = $("#mongo_db").val();
    var collection = $("#mongo_collection").val();
    var filter_field = $("#mongo_filter_field").val();
    var index = $("#elasticsearch_index").val();
    var doc_type = $("#elasticsearch_doc_type").val();
    var use_mongo_id = $("#use_mongo_id").prop("checked");
    var success_count = 0;
    var fail_count = 0;
    var success_flag = false;
    var request_flag = true;
    var eventSource = null;
    var percentage = 0;

    if (host === "" || port === "" || db === "" || collection === "" || index === "" || doc_type === "") {
        return;
    }

    // Listen event from server then dynamic modify progress bar
    if (typeof (EventSource) !== "undefined") {
        eventSource = new EventSource("/supervisor/elasticsearch/transfer/progress");
        eventSource.onerror = function (event) {
            eventSource.close();
            console.log('Acquire progress data failure because SSE connection have is interrupted.');
            if (success_flag) {
                swal("Good job!", "Transfer data have complete! Success: " + success_count + " Failure: " + fail_count, "success");
            } else {
                swal("Oops!", "An exception occurred in inside of the server!", "error");
            }
        };
        eventSource.onmessage = function (event) {
            if (event.data === "error") {
                eventSource.close();
            } else {
                percentage = event.data;
                $("#progress_bar").css("width", percentage + "%").text(percentage + "%");
            }
        };
    } else {
        swal("Oops!", "Sorry, your browser do not supply this function.", "error");
        console.log("Your browser do not supply Server-Sent-Event.");
    }

    // Send asynchronous request for enable data transfer
    $.ajax({
        url: "/supervisor/elasticsearch/enable/transfer",
        type: "POST",
        data: {
            "mongo_host": host,
            "mongo_port": port,
            "mongo_db": db,
            "mongo_collection": collection,
            "filter_field": filter_field,
            "elasticsearch_index": index,
            "elasticsearch_doc_type": doc_type,
            "use_mongo_id": use_mongo_id
        },
        success: function (data) {
            success_count = data.success_count;
            fail_count = data.fail_count;
            success_flag = true;
        },
        error: function (xhr, message, throwable) {
            swal("Oops!", "Sorry, request is the failure then connection interrupt.", "error");
            console.log(message);
            console.log(throwable);
            request_flag = false;
        }
    });

    if (!request_flag && eventSource !== null) {
        eventSource.close();
    }
}

function enable_auto_transfer() {
    var host = $("#auto_mongo_host").val();
    var port = $("#auto_mongo_port").val();
    var db = $("#auto_mongo_db").val();
    var collection = $("#auto_mongo_collection").val();
    var filter_field = $("#auto_mongo_filter_field").val();
    var index = $("#auto_elasticsearch_index").val();
    var doc_type = $("#auto_elasticsearch_doc_type").val();
    var use_mongo_id = $("#auto_use_mongo_id").prop("checked");
    var interval = parseInt($("#interval_time").val());

    if (host === "" || port === "" || db === "" || collection === "" ||
        index === "" || doc_type === "" || filter_field === "") {
        return;
    }

    $.ajax({
        url: "/supervisor/elasticsearch/enable/auto/transfer",
        type: "POST",
        data: {
            "mongo_host": host,
            "mongo_port": port,
            "mongo_db": db,
            "mongo_collection": collection,
            "filter_field": filter_field,
            "elasticsearch_index": index,
            "elasticsearch_doc_type": doc_type,
            "use_mongo_id": use_mongo_id,
            "interval": interval
        },
        success: function (data) {
            if (data.status === "success") {
                swal("Good job!", "Enable automatic data transfer is success!", "success");
            } else {
                swal("Oops!", "Enable automatic data transfer is failed!", "error");
            }
        },
        error: function (xhr, message, throwable) {
            console.log(message);
            console.log(throwable);
            swal("Oops!", "Enable automatic data transfer is failed!", "error");
        }
    });

    location.reload();
}

function cancel_auto_transfer() {
    $.ajax({
        url: "/supervisor/elasticsearch/cancel/auto/transfer",
        type: "POST",
        success: function (data) {
            if (data.status === "success") {
                swal("Good job!", "Cancel automatic data transfer is success!", "success");
            } else {
                swal("Oops!", "Cancel automatic data transfer is failed!", "error");
            }
        },
        error: function (xhr, message, throwable) {
            console.log(message);
            console.log(throwable);
            swal("Oops!", "Cancel automatic data transfer is failed!", "error");
        }
    });

    location.reload();
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
                "data-target='#transfer_data_modal'  class='btn btn-outline-primary'>" +
                "<i class='fa fa-magic mr-1'></i>Manual Transfer</button>");
            var auto_transfer_button = $("<button type='button' data-toggle='modal' " +
                "data-target='#auto_transfer_data_modal' class='btn btn-outline-info'>" +
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
                "you can choose means for transfer data from MongoDB into the Elasticsearch." +
                "There is a optional option for filter data in the form that is a text " +
                "of the field name(must existence in MongoDB document) and this type must " +
                "is a boolean this will not transfer into the Elasticsearch if it's false.");
        } else {
            transfer_data_card_text.text("The current status is automatically transmitted data " +
                "with synchronized from MongoDB.");
            transfer_data_card_body.append($("<button onclick='cancel_auto_transfer()' type='button' " +
                "class='btn btn-outline-danger'><i class='fa fa-magic mr-1'></i>Cancel</button>"));
        }
    }
});

$("#transfer_data_modal_form").bootstrapValidator({
    message: "This value is not valid.",
    feedbackIcons: {
        valid: 'glyphicon glyphicon-ok',
        invalid: 'glyphicon glyphicon-remove',
        validating: 'glyphicon glyphicon-refresh'
    },
    fields: {
        mongo_host: {
            message: "The MongoDB host validate failure!",
            validators: {
                notEmpty: {
                    message: "The MongoDB host must is not empty!"
                }
            }
        },
        mongo_port: {
            message: "The MongoDB port validate failure!",
            validators: {
                notEmpty: {
                    message: "The MongoDB port must is not empty!"
                }
            }
        },
        mongo_db: {
            message: "The MongoDB database validate failure!",
            validators: {
                notEmpty: {
                    message: "The MongoDB database must is not empty!"
                }
            }
        },
        mongo_collection: {
            message: "The MongoDB collection validate failure!",
            validators: {
                notEmpty: {
                    message: "The MongoDB collection must is not empty!"
                }
            }
        },
        elasticsearch_index: {
            message: "The Elasticsearch index validate failure!",
            validators: {
                notEmpty: {
                    message: "The Elasticsearch index must is not empty!"
                }
            }
        },
        elasticsearch_doc_type: {
            message: "The Elasticsearch document type validate failure!",
            validators: {
                notEmpty: {
                    message: "The Elasticsearch document type must is not empty!"
                }
            }
        }
    }
});

$("#auto_transfer_data_modal_form").bootstrapValidator({
    message: "This value is not valid.",
    feedbackIcons: {
        valid: 'glyphicon glyphicon-ok',
        invalid: 'glyphicon glyphicon-remove',
        validating: 'glyphicon glyphicon-refresh'
    },
    fields: {
        auto_mongo_host: {
            message: "The MongoDB host validate failure!",
            validators: {
                notEmpty: {
                    message: "The MongoDB host must is not empty!"
                }
            }
        },
        auto_mongo_port: {
            message: "The MongoDB port validate failure!",
            validators: {
                notEmpty: {
                    message: "The MongoDB port must is not empty!"
                }
            }
        },
        auto_mongo_db: {
            message: "The MongoDB database validate failure!",
            validators: {
                notEmpty: {
                    message: "The MongoDB database must is not empty!"
                }
            }
        },
        auto_mongo_collection: {
            message: "The MongoDB collection validate failure!",
            validators: {
                notEmpty: {
                    message: "The MongoDB collection must is not empty!"
                }
            }
        },
        auto_elasticsearch_index: {
            message: "The Elasticsearch index validate failure!",
            validators: {
                notEmpty: {
                    message: "The Elasticsearch index must is not empty!"
                }
            }
        },
        auto_elasticsearch_doc_type: {
            message: "The Elasticsearch document type validate failure!",
            validators: {
                notEmpty: {
                    message: "The Elasticsearch document type must is not empty!"
                }
            }
        },
        auto_mongo_filter_field: {
            message: "The MongoDB filter field name validate failure!",
            validators: {
                notEmpty: {
                    message: "The MongoDB filter field name must is not empty!"
                }
            }
        }
    }
});