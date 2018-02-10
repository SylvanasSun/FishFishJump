function handle_nodes_basic(data) {
    $("#nodes_basic_li_failed").children("span").text(data.failed);
    $("#nodes_basic_li_successful").children("span").text(data.successful);
    $("#nodes_basic_li_total").children("span").text(data.total);
}

function handle_nodes_count(data) {
    $("#nodes_count_li_coordinating_only").children("span").text(data.coordinating_only);
    $("#nodes_count_li_data").children("span").text(data.data);
    $("#nodes_count_li_ingest").children("span").text(data.ingest);
    $("#nodes_count_li_master").children("span").text(data.master);
    $("#nodes_count_li_total").children("span").text(data.total);
}

function handle_nodes_fs(data) {
    $("#nodes_fs_li_available_in_bytes").children("span").text(byte_to_gb(data.available_in_bytes, 4) + " GB");
    $("#nodes_fs_li_free_in_bytes").children("span").text(byte_to_gb(data.free_in_bytes, 4) + " GB");
    $("#nodes_fs_li_total_in_bytes").children("span").text(byte_to_gb(data.total_in_bytes, 4) + " GB");
}

function handle_nodes_os(data) {
    $("#nodes_os_li_allocated_processors").children("span").text(data.allocated_processors);
    $("#nodes_os_li_available_processors").children("span").text(data.available_processors);
    $("#nodes_os_li_mem_free_in_bytes").children("span").text(byte_to_gb(data.mem.free_in_bytes, 4) + " GB");
    $("#nodes_os_li_mem_free_percent").children("span").text(data.mem.free_percent + "%");
    $("#nodes_os_li_mem_used_in_bytes").children("span").text(byte_to_gb(data.mem.used_in_bytes, 4) + " GB");
    $("#nodes_os_li_mem_used_percent").children("span").text(data.mem.used_percent + "%");
    $("#nodes_os_li_mem_total_in_bytes").children("span").text(byte_to_gb(data.mem.total_in_bytes, 4) + " GB");
    var ul = $("#nodes_os_li_names");
    ul.children().remove();
    for (var i = 0; i < data.names.length; i++) {
        var li = $("<li class='list-group-item d-flex justify-content-between align-items-center'>" +
            data.names[i].name + "</li>");
        li.append($("<span class='badge badge-primary badge-pill'>" + data.names[i].count + "</span>"));
        ul.append(li);
    }

    var available_cpu_processor_percentage_val = ((data.available_processors / data.allocated_processors) * 100).toFixed(2);
    var availiable_cpu_processor_percentage = $("#available_cpu_processor_percentage");
    availiable_cpu_processor_percentage.children("span").text(available_cpu_processor_percentage_val + "%");
    availiable_cpu_processor_percentage.attr("class", "c100 p" + Math.round(available_cpu_processor_percentage_val) + " big center");

    var free_memory_percentage_val = data.mem.free_percent;
    var free_memory_percentage = $("#free_memory_percentage");
    free_memory_percentage.children("span").text(free_memory_percentage_val + "%");
    free_memory_percentage.attr("class", "c100 p" + Math.round(free_memory_percentage_val) + " big center");

    var used_memory_percentage_val = data.mem.used_percent;
    var used_memory_percentage = $("#used_memory_percentage");
    used_memory_percentage.children("span").text(used_memory_percentage_val + "%");
    used_memory_percentage.attr("class", "c100 p" + Math.round(used_memory_percentage_val) + " big center");
}

function handle_nodes_jvm(data) {
    $("#nodes_jvm_li_max_uptime_in_millis").children("span").text(data.max_uptime_in_millis + " ms");
    $("#nodes_jvm_li_threads").children("span").text(data.threads);
    $("#nodes_jvm_li_mem_heap_max_in_bytes").children("span").text(byte_to_mb(data.mem.heap_max_in_bytes, 4) + " MB");
    $("#nodes_jvm_li_mem_heap_used_in_bytes").children("span").text(byte_to_mb(data.mem.heap_used_in_bytes, 4) + " MB");
    var ul = $("#nodes_jvm_li_versions");
    ul.children().remove();
    var counter = {};
    for (var i = 0; i < data.versions.length; i++) {
        var versions = data.versions[i];
        for (var x in versions) {
            if (x !== "count") {
                var name = x + ": " + versions[x];
                if (typeof(counter[name]) === "undefined") {
                    counter[name] = 1;
                } else {
                    counter[name] = counter[name] + 1;
                }
            }
        }
    }
    for (var x in counter) {
        var li = $("<li class='list-group-item d-flex justify-content-between align-items-center'>" + x + "</li>");
        li.append($("<span class='badge badge-primary badge-pill'>" + counter[x] + "</span>"));
        ul.append(li);
    }

    var used_jvm_heap_memory_percentage_val = ((data.mem.heap_used_in_bytes / data.mem.heap_max_in_bytes) * 100).toFixed(2);
    var used_jvm_heap_memory_percentage = $("#used_jvm_heap_memory_percentage");
    used_jvm_heap_memory_percentage.children("span").text(used_jvm_heap_memory_percentage_val + "%");
    used_jvm_heap_memory_percentage.attr("class", "c100 p" + Math.round(used_jvm_heap_memory_percentage_val) + " big center");
}

function handle_nods_other(data) {
    var http_types = data.network_types.http_types;
    for (var x in http_types) {
        $("#nodes_other_li_network_types_http_types").children("span").text(x + ": " + http_types[x]);
    }
    var transport_types = data.network_types.transport_types;
    for (var x in transport_types) {
        $("#nodes_other_li_network_types_transport_types").children("span").text(x + ": " + transport_types[x]);
    }

    $("#nodes_other_li_process_cpu_percent").children("span").text(data.process.cpu.percent + "%");
    $("#nodes_other_li_open_file_descriptors_avg").children("span").text(data.process.open_file_descriptors.avg);
    $("#nodes_other_li_open_file_descriptors_max").children("span").text(data.process.open_file_descriptors.max);
    $("#nodes_other_li_open_file_descriptors_min").children("span").text(data.process.open_file_descriptors.min);

    var plugins = data.plugins;
    var plugins_ul = $("#nodes_other_li_plugins");
    plugins_ul.children().remove();
    for (var i = 0; i < plugins.length; i++) {
        var li = $("<li class='list-group-item d-flex justify-content-between align-items-center'></li>");
        li.append($("<span>" + plugins[i] + "</span>"));
        plugins_ul.append(li);
    }

    var versions = data.versions;
    var versions_ul = $("#nodes_other_li_versions");
    versions_ul.children().remove();
    for (var i = 0; i < versions.length; i++) {
        var li = $("<li class='list-group-item d-flex justify-content-between align-items-center'></li>");
        li.append($("<span>" + versions[i] + "</span>"));
        versions_ul.append(li);
    }
}

function handle_indices_basic(data) {
    $("#indices_basic_li_completion_size_in_bytes").children("span").text(data.completion.size_in_bytes);
    $("#indices_basic_li_count").children("span").text(data.count);
    $("#indices_basic_li_docs_count").children("span").text(data.docs.count);
    $("#indices_basic_li_docs_deleted").children("span").text(data.docs.deleted);
    $("#indices_basic_li_fielddata_evictions").children("span").text(data.fielddata.evictions);
    $("#indices_basic_li_fielddata_memory_size_in_bytes").children("span").text(data.fielddata.memory_size_in_bytes);
    $("#indices_basic_li_store").children("span").text(data.store.size_in_bytes);
}

function handle_indices_query_cache(data) {
    $("#indices_query_li_cache_count").children("span").text(data.cache_count);
    $("#indices_query_li_cache_size").children("span").text(data.cache_size);
    $("#indices_query_li_evictions").children("span").text(data.evictions);
    $("#indices_query_li_hit_count").children("span").text(data.hit_count);
    $("#indices_query_li_memory_size_in_bytes").children("span").text(data.memory_size_in_bytes);
    $("#indices_query_li_miss_count").children("span").text(data.miss_count);
    $("#indices_query_li_total_count").children("span").text(data.total_count);
}

function handle_indices_segments(data) {
    $("#indices_segments_li_count").children("span").text(data.count);
    $("#indices_segments_li_doc_values_memory_in_bytes").children("span").text(data.doc_values_memory_in_bytes);
    $("#indices_segments_li_fixed_bit_set_memory_in_bytes").children("span").text(data.fixed_bit_set_memory_in_bytes);
    $("#indices_segments_li_index_writer_memory_in_bytes").children("span").text(data.index_writer_memory_in_bytes);
    $("#indices_segments_li_max_unsafe_auto_id_timestamp").children("span").text(data.max_unsafe_auto_id_timestamp);
    $("#indices_segments_li_memory_in_bytes").children("span").text(data.memory_in_bytes);
    $("#indices_segments_li_norms_memory_in_bytes").children("span").text(data.norms_memory_in_bytes);
    $("#indices_segments_li_points_memory_in_bytes").children("span").text(data.points_memory_in_bytes);
    $("#indices_segments_li_stored_fields_memory_in_bytes").children("span").text(data.stored_fields_memory_in_bytes);
    $("#indices_segments_li_term_vectors_memory_in_bytes").children("span").text(data.term_vectors_memory_in_bytes);
    $("#indices_segments_li_terms_memory_in_bytes").children("span").text(data.terms_memory_in_bytes);
    $("#indices_segments_li_version_map_memory_in_bytes").children("span").text(data.version_map_memory_in_bytes);

    var file_sizes_ul = $("#indices_segments_li_file_sizes");
    var file_size = data.file_sizes;
    file_sizes_ul.children().remove();
    for (var x in file_size) {
        var li = $("<li class='list-group-item d-flex justify-content-between align-items-center'>" + x + "</li>");
        li.append($("<span class='badge badge-primary badge-pill'>" + file_size[x] + "</span>"));
        file_sizes_ul.append(li);
    }
}

function handle_indices_shards(data) {
    $("#indices_shards_li_primaries_count").children("span").text(data.primaries);
    $("#indices_shards_li_replication_count").children("span").text(data.replication);
    $("#indices_shards_li_total_count").children("span").text(data.total);
    $("#indices_shards_li_primaries_avg").children("span").text(data.index.primaries.avg);
    $("#indices_shards_li_primaries_max").children("span").text(data.index.primaries.max);
    $("#indices_shards_li_primaries_min").children("span").text(data.index.primaries.min);
    $("#indices_shards_li_replication_avg").children("span").text(data.index.replication.avg);
    $("#indices_shards_li_replication_max").children("span").text(data.index.replication.max);
    $("#indices_shards_li_replication_min").children("span").text(data.index.replication.min);
    $("#indices_shards_li_shards_avg").children("span").text(data.index.shards.avg);
    $("#indices_shards_li_shards_max").children("span").text(data.index.shards.max);
    $("#indices_shards_li_shards_min").children("span").text(data.index.shards.min);
}

function ajax_cluster_stats() {
    $.ajax({
        url: "/elasticsearch/cluster/stats",
        type: "GET",
        success: function (data) {
            timeout_alert(data[polling_info.failure_message_key]);
            handle_nodes_basic(data._nodes);
            handle_nodes_count(data.nodes.count);
            handle_nodes_fs(data.nodes.fs);
            handle_nodes_os(data.nodes.os);
            handle_nodes_jvm(data.nodes.jvm);
            handle_nods_other(data.nodes);
            handle_indices_basic(data.indices);
            handle_indices_query_cache(data.indices.query_cache);
            handle_indices_segments(data.indices.segments);
            handle_indices_shards(data.indices.shards);
        },
        error: function (xhr, message, throwable) {
            ajax_error_alert(xhr.status, message);
        }
    });
}

invoke_polling(ajax_cluster_stats);
