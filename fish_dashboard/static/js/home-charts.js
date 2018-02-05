function ajax_home_charts() {
    var scrapyd_status_obj = {};

    $.ajax({
        url: "/scrapyd/status/chart",
        type: "GET",
        success: function (data) {
            timeout_alert(data[polling_info.failure_message_key]);
            $("#project_amount").text(data.project_amount);
            $("#spider_amount").text(data.spider_amount);
            $("#job_amount").text(data.job_amount);
            scrapyd_status_obj = data;
        },
        error: function (xhr, message, throwable) {
            ajax_error_alert(xhr.status, message);
        }
    });

    var bar_chart_ctx = document.getElementById("scrapy_status_bar_chart");
    var scrapydStatusChart = new Chart(bar_chart_ctx, {
        type: 'bar',
        data: {
            labels: ["Running", "Pending", "Finished"],
            datasets: [{
                label: "Amount",
                backgroundColor: "rgba(2,117,216,1)",
                borderColor: "rgba(2,117,216,1)",
                data: [scrapyd_status_obj.running, scrapyd_status_obj.pending, scrapyd_status_obj.finished]
            }]
        },
        options: {
            scales: {
                xAxes: [{
                    time: {
                        unit: 'amount'
                    },
                    gridLines: {
                        display: false
                    },
                    ticks: {
                        maxTicksLimit: 3
                    }
                }],
                yAxes: [{
                    ticks: {
                        min: 0,
                        max: scrapyd_status_obj.running + scrapyd_status_obj.pending + scrapyd_status_obj.finished + 20,
                        maxTicksLimit: 5
                    },
                    gridLines: {
                        display: true
                    }
                }]
            },
            legend: {
                display: false
            }
        }
    });

    var pie_ctx = document.getElementById("scrapy_status_pie_chart");
    var myPieChart = new Chart(pie_ctx, {
        type: 'pie',
        data: {
            labels: ["Running", "Pending", "Finished"],
            datasets: [{
                data: [scrapyd_status_obj.running, scrapyd_status_obj.pending, scrapyd_status_obj.finished],
                backgroundColor: ['#007bff', '#dc3545', '#ffc107']
            }]
        }
    });
}

invoke_polling(ajax_home_charts);