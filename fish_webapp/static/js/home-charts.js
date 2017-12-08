var scrapyd_status_obj = {};
get_scrapyd_status();

var ctx = document.getElementById("scrapy_status_bar_chart");
var scrapydStatusChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ["Running", "Pending", "Finished"],
        datasets: [{
            label: "Amount",
            backgroundColor: "rgba(2,117,216,1)",
            borderColor: "rgba(2,117,216,1)",
            data: [scrapyd_status_obj.running, scrapyd_status_obj.pending, scrapyd_status_obj.finished],
        }],
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
                    max: 100,
                    maxTicksLimit: 5
                },
                gridLines: {
                    display: true
                }
            }],
        },
        legend: {
            display: false
        }
    }
});

var ctx = document.getElementById("scrapy_status_pie_chart");
var myPieChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: ["Running", "Pending", "Finished"],
        datasets: [{
            data: [scrapyd_status_obj.running, scrapyd_status_obj.pending, scrapyd_status_obj.finished],
            backgroundColor: ['#007bff', '#dc3545', '#ffc107'],
        }],
    },
});

function get_scrapyd_status() {
    $.ajax({
        url: "/supervisor/scrapyd/status/chart",
        type: "GET",
        async: false,
        success: function (data) {
            $("#project_amount").text(data.project_amount);
            $("#spider_amount").text(data.spider_amount);
            $("#job_amount").text(data.job_amount);
            scrapyd_status_obj = data;
        }
    });
}