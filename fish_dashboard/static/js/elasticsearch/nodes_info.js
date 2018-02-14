function ajax_nodes_simple_info() {
    $.ajax({
        url: "/elasticsearch/nodes/simple/info",
        type: "GET",
        success: function (data) {
            timeout_alert(data[polling_info.failure_message_key]);
            var tbody = $("#elasticsearch_nodes_info_tbody");
            tbody.children().remove();
            for (var i = 0; i < data.length; i++) {
                var tr = $("<tr></tr>");
                tr.append($("<th scope='row'>" + (i + 1) + "</th>"));
                tr.append($("<td>" + data[i].name + "</td>"));
                tr.append($("<td>" + data[i].pid + "</td>"));
                tr.append($("<td>" + data[i].http_address + "</td>"));
                tr.append($("<td>" + data[i].version + "</td>"));
                tr.append($("<td>" + data[i].jdk + "</td>"));
                tr.append($("<td><span class='badge badge-pill badge-success'>" + data[i]['disk.total'] + "</span></td>"));
                tr.append($("<td><span class='badge badge-pill badge-info'>" + data[i]['disk.used_percent'] + "%</span></td>"));
                tr.append($("<td><span class='badge badge-pill badge-success'>" + data[i]['heap.current'] + "</span></td>"));
                tr.append($("<td><span class='badge badge-pill badge-info'>" + data[i]['heap.percent'] + "%</span></td>"));
                tr.append($("<td><span class='badge badge-pill badge-success'>" + data[i]['ram.current'] + "</span></td>"));
                tr.append($("<td><span class='badge badge-pill badge-info'>" + data[i]['ram.percent'] + "%</span></td>"));
                tr.append($("<td><span class='badge badge-pill badge-success'>" + data[i].uptime + "</span></td>"));
                tr.append($("<td><span class='badge badge-pill badge-primary'>" + data[i]['node.role'] + "</span></td>"));
                tr.append($("<td><button class='btn btn-outline-primary' onclick='open_nodes_stats(\"" + data[i].name + "\")'>Detail</button></td>"));
                tbody.append(tr);
            }
        },
        error: function (xhr, message, throwable) {
            ajax_error_alert(xhr.status, message);
        }
    })
}

function handle_fs(fs) {
    var data_body = $("#nodes_stats_fs_content_data_body");
    data_body.children().remove();
    var data_ul = $("<ul class='list-group list-group-flush'></ul>");
    for (var i = 0; i < fs['data'].length; i++) {
        for (var key in fs['data'][i]) {
            var li = $("<li class='list-group-item'><h5>" + key + "</h5></li>");
            li.append($("<span class='badge badge-primary badge-pill'>" + fs['data'][i][key] + "</span>"));
            data_ul.append(li);
        }
        data_body.append(data_ul);
    }

    $("#nodes_stats_fs_content_least").on("shown.bs.tab", function (e) {
        generate_ul_under_body("least_usage_estimate", fs, "nodes_stats_fs_content_least_body", true);
    });

    $("#nodes_stats_fs_content_most").on("shown.bs.tab", function (e) {
        generate_ul_under_body("most_usage_estimate", fs, "nodes_stats_fs_content_most_body", true);
    });

    $("#nodes_stats_fs_content_total").on("shown.bs.tab", function (e) {
        generate_ul_under_body("total", fs, "nodes_stats_fs_content_total_body", true);
    });
}

function handle_os(os) {
    generate_ul_under_body("mem", os, "nodes_stats_os_content_mem_body", true);

    $("#nodes_stats_os_content_swap").on("shown.bs.tab", function (e) {
        generate_ul_under_body("swap", os, "nodes_stats_os_content_swap_body", true);
    });

    $("#nodes_stats_os_content_cpu").on("shown.bs.tab", function (e) {
        generate_ul_under_body("cpu", os, "nodes_stats_os_content_cpu_body", true);
    });
}

function handle_thread_pool(thread_pool) {
    generate_ul_under_body("bulk", thread_pool, "nodes_stats_thread_pool_content_bulk_body", true);

    $("#nodes_stats_thread_pool_content_fetch_shard_started").on("shown.bs.tab", function (e) {
        generate_ul_under_body("fetch_shard_started", thread_pool, "nodes_stats_thread_pool_content_fetch_shard_started_body", true);
    });

    $("#nodes_stats_thread_pool_content_fetch_shard_store").on("shown.bs.tab", function (e) {
        generate_ul_under_body("fetch_shard_store", thread_pool, "nodes_stats_thread_pool_content_fetch_shard_store_body", true);
    });

    $("#nodes_stats_thread_pool_content_flush").on("shown.bs.tab", function (e) {
        generate_ul_under_body("flush", thread_pool, "nodes_stats_thread_pool_content_flush_body", true);
    });

    $("#nodes_stats_thread_pool_content_force_merge").on("shown.bs.tab", function (e) {
        generate_ul_under_body("force_merge", thread_pool, "nodes_stats_thread_pool_content_force_merge_body", true);
    });

    $("#nodes_stats_thread_pool_content_generic").on("shown.bs.tab", function (e) {
        generate_ul_under_body("generic", thread_pool, "nodes_stats_thread_pool_content_generic_body", true);
    });

    $("#nodes_stats_thread_pool_content_get").on("shown.bs.tab", function (e) {
        generate_ul_under_body("get", thread_pool, "nodes_stats_thread_pool_content_get_body", true);
    });

    $("#nodes_stats_thread_pool_content_index").on("shown.bs.tab", function (e) {
        generate_ul_under_body("index", thread_pool, "nodes_stats_thread_pool_content_index_body", true);
    });

    $("#nodes_stats_thread_pool_content_listener").on("shown.bs.tab", function (e) {
        generate_ul_under_body("listener", thread_pool, "nodes_stats_thread_pool_content_listener_body", true);
    });

    $("#nodes_stats_thread_pool_content_management").on("shown.bs.tab", function (e) {
        generate_ul_under_body("management", thread_pool, "nodes_stats_thread_pool_content_management_body", true);
    });

    $("#nodes_stats_thread_pool_content_refresh").on("shown.bs.tab", function (e) {
        generate_ul_under_body("refresh", thread_pool, "nodes_stats_thread_pool_content_refresh_body", true);
    });

    $("#nodes_stats_thread_pool_content_search").on("shown.bs.tab", function (e) {
        generate_ul_under_body("search", thread_pool, "nodes_stats_thread_pool_content_search_body", true);
    });

    $("#nodes_stats_thread_pool_content_snapshot").on("shown.bs.tab", function (e) {
        generate_ul_under_body("snapshot", thread_pool, "nodes_stats_thread_pool_content_snapshot_body", true);
    });

    $("#nodes_stats_thread_pool_content_warmer").on("shown.bs.tab", function (e) {
        generate_ul_under_body("warmer", thread_pool, "nodes_stats_thread_pool_content_warmer_body", true);
    });
}

function handle_breakers(breakers) {
    generate_ul_under_body("fielddata", breakers, "nodes_stats_breakers_content_fielddata_body", true);

    $("#nodes_stats_breakers_content_in_flight_requests").on("shown.bs.tab", function (e) {
        generate_ul_under_body("in_flight_requests", breakers, "nodes_stats_breakers_content_in_flight_requests_body", true);
    });

    $("#nodes_stats_breakers_content_parent").on("shown.bs.tab", function (e) {
        generate_ul_under_body("parent", breakers, "nodes_stats_breakers_content_parent_body", true);
    });

    $("#nodes_stats_breakers_content_request").on("shown.bs.tab", function (e) {
        generate_ul_under_body("request", breakers, "nodes_stats_breakers_content_request_body", true);
    });
}

function handle_jvm(jvm) {
    generate_ul_under_body("direct", jvm['buffer_pools'], "nodes_stats_jvm_content_buffer_pools_direct_body", true);

    $("#nodes_stats_jvm_content_buffer_pools_mapped").on("shown.bs.tab", function (e) {
        generate_ul_under_body("mapped", jvm['buffer_pools'], "nodes_stats_jvm_content_buffer_pools_mapped_body", true);
    });

    $("#nodes_stats_jvm_content_classes").on("shown.bs.tab", function (e) {
        generate_ul_under_body("classes", jvm, "nodes_stats_jvm_content_classes_body", true);
    });

    $("#nodes_stats_jvm_content_gc_old").on("shown.bs.tab", function (e) {
        generate_ul_under_body("old", jvm['gc']['collectors'], "nodes_stats_jvm_content_gc_old_body", true);
    });

    $("#nodes_stats_jvm_content_gc_young").on("shown.bs.tab", function (e) {
        generate_ul_under_body("young", jvm['gc']['collectors'], "nodes_stats_jvm_content_gc_young_body", true);
    });

    $("#nodes_stats_jvm_content_mem").on("shown.bs.tab", function (e) {
        var body = $("#nodes_stats_jvm_content_mem_body");
        body.children().remove();
        var ul = $("<ul class='list-group list-group-flush'></ul>");
        for (var key in jvm['mem']) {
            if (key !== "pools") {
                var li = $("<li class='list-group-item'><h5>" + key + "</h5></li>");
                li.append($("<span class='badge badge-primary badge-pill'>" + jvm['mem'][key] + "</span>"));
                ul.append(li);
            }
        }
        body.append(ul);
    });

    $("#nodes_stats_jvm_content_mem_pools_old").on("shown.bs.tab", function (e) {
        generate_ul_under_body("old", jvm['mem']['pools'], "nodes_stats_jvm_content_mem_pools_old_body", true);
    });

    $("#nodes_stats_jvm_content_mem_pools_survivor").on("shown.bs.tab", function (e) {
        generate_ul_under_body("survivor", jvm['mem']['pools'], "nodes_stats_jvm_content_mem_pools_survivor_body", true);
    });

    $("#nodes_stats_jvm_content_mem_pools_young").on("shown.bs.tab", function (e) {
        generate_ul_under_body("young", jvm['mem']['pools'], "nodes_stats_jvm_content_mem_pools_young_body", true);
    });

    $("#nodes_stats_jvm_content_threads").on("shown.bs.tab", function (e) {
        generate_ul_under_body("threads", jvm, "nodes_stats_jvm_content_threads_body", true);
    });

    $("#nodes_stats_jvm_content_other").on("shown.bs.tab", function (e) {
        var body = $("#nodes_stats_jvm_content_other_body");
        body.children().remove();
        var ul = $("<ul class='list-group list-group-flush'></ul>");
        var li = $("<li class='list-group-item'><h5>uptime_in_millis</h5></li>");
        li.append($("<span class='badge badge-primary badge-pill'>" + jvm['uptime_in_millis'] + "</span>"));
        ul.append(li);
        body.append(ul);
    });
}

function handle_indices(indices) {
    generate_ul_under_body("completion", indices, "nodes_stats_indices_content_completion_body", true);

    $("#nodes_stats_indices_content_docs").on("shown.bs.tab", function (e) {
        generate_ul_under_body("docs", indices, "nodes_stats_indices_content_docs_body", true);
    });

    $("#nodes_stats_indices_content_fielddata").on("shown.bs.tab", function (e) {
        generate_ul_under_body("fielddata", indices, "nodes_stats_indices_content_fielddata_body", true);
    });

    $("#nodes_stats_indices_content_flush").on("shown.bs.tab", function (e) {
        generate_ul_under_body("flush", indices, "nodes_stats_indices_content_flush_body", true);
    });

    $("#nodes_stats_indices_content_get").on("shown.bs.tab", function (e) {
        generate_ul_under_body("get", indices, "nodes_stats_indices_content_get_body", true);
    });

    $("#nodes_stats_indices_content_indexing").on("shown.bs.tab", function (e) {
        generate_ul_under_body("indexing", indices, "nodes_stats_indices_content_indexing_body", true);
    });

    $("#nodes_stats_indices_content_merges").on("shown.bs.tab", function (e) {
        generate_ul_under_body("merges", indices, "nodes_stats_indices_content_merges_body", true);
    });

    $("#nodes_stats_indices_content_query_cache").on("shown.bs.tab", function (e) {
        generate_ul_under_body("query_cache", indices, "nodes_stats_indices_content_query_cache_body", true);
    });

    $("#nodes_stats_indices_content_recovery").on("shown.bs.tab", function (e) {
        generate_ul_under_body("recovery", indices, "nodes_stats_indices_content_recovery_body", true);
    });

    $("#nodes_stats_indices_content_refresh").on("shown.bs.tab", function (e) {
        generate_ul_under_body("refresh", indices, "nodes_stats_indices_content_refresh_body", true);
    });

    $("#nodes_stats_indices_content_request_cache").on("shown.bs.tab", function (e) {
        generate_ul_under_body("request_cache", indices, "nodes_stats_indices_content_request_cache_body", true);
    });

    $("#nodes_stats_indices_content_search").on("shown.bs.tab", function (e) {
        generate_ul_under_body("search", indices, "nodes_stats_indices_content_search_body", true);
    });

    $("#nodes_stats_indices_content_segments").on("shown.bs.tab", function (e) {
        generate_ul_under_body("segments", indices, "nodes_stats_indices_content_segments_body", true);
    });

    $("#nodes_stats_indices_content_store").on("shown.bs.tab", function (e) {
        generate_ul_under_body("store", indices, "nodes_stats_indices_content_store_body", true);
    });

    $("#nodes_stats_indices_content_translog").on("shown.bs.tab", function (e) {
        generate_ul_under_body("translog", indices, "nodes_stats_indices_content_translog_body", true);
    });

    $("#nodes_stats_indices_content_warmer").on("shown.bs.tab", function (e) {
        generate_ul_under_body("warmer", indices, "nodes_stats_indices_content_warmer_body", true);
    });
}

function open_nodes_stats(node_name) {
    $("#nodes_stats_modal_title").text("Node Stats (" + node_name + ")");
    $.ajax({
        url: "/elasticsearch/nodes/stats/" + node_name,
        type: "GET",
        success: function (data) {
            timeout_alert(data[polling_info.failure_message_key]);
            var nodes_stats = data.nodes;
            var nodes = null;
            for (var nodes_key in nodes_stats) {
                nodes = nodes_stats[nodes_key];
            }

            handle_fs(nodes['fs']);
            handle_os(nodes['os']);
            handle_thread_pool(nodes['thread_pool']);
            handle_breakers(nodes['breakers']);
            handle_jvm(nodes['jvm']);
            handle_indices(nodes['indices']);
        },
        error: function (xhr, message, throwable) {
            ajax_error_alert(xhr.status, message);
        }
    });
    $("#nodes_stats_modal").modal("show");
}

invoke_polling(ajax_nodes_simple_info);