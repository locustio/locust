var newTestLink = $("#new-test");
var editTestLink = $("#edit-test");

$(window).ready(function() {
    if($("#user_count").length > 0) {
        $("#user_count").focus().select();
    }
});

function appearStopped() {
    $(".box_stop").hide();
    newTestLink.show();
    editTestLink.hide();
    $(".user_count").hide();
}

$("#box_stop a.stop-button").click(function(event) {
    event.preventDefault();
    $.get($(this).attr("href"));
    $("body").attr("class", "stopped");
    appearStopped()
});

$("#box_stop a.reset-button").click(function(event) {
    event.preventDefault();
    $.get($(this).attr("href"));
});

newTestLink.click(function(event) {
    event.preventDefault();
    $("#start").show();
    $("#user_count").focus().select();
});

editTestLink.click(function(event) {
    event.preventDefault();
    $("#edit").show();
    $("#new_user_count").focus().select();
});

$(".close_link").click(function(event) {
    event.preventDefault();
    $(this).parent().parent().hide();
});

$("ul.tabs").tabs("div.panes > div").on("onClick", function (event) {
    // trigger resizing of charts
    resizeCharts();
});

var charts = []
function resizeCharts() {
    for (let index = 0; index < charts.length; index++) {
        const chart = charts[index];
        chart.resize();
    }
}

var stats_tpl = $('#stats-template');
var errors_tpl = $('#errors-template');
var exceptions_tpl = $('#exceptions-template');
var workers_tpl = $('#worker-template');

function setHostName(hostname) {
    hostname = hostname || "";
    $('#host_url').text(hostname);
}

$('#swarm_form').submit(function(event) {
    event.preventDefault();
    $("body").attr("class", "spawning");
    $("#start").hide();
    $("#main").show();
    $(".box_running").show();
    newTestLink.hide();
    editTestLink.show();
    $(".user_count").show();
    $.post($(this).attr("action"), $(this).serialize(),
        function(response) {
            if (response.success) {
                setHostName(response.host);
            }
        }
    );
});

$('#edit_form').submit(function(event) {
    event.preventDefault();
    $.post($(this).attr("action"), $(this).serialize(),
        function(response) {
            if (response.success) {
                $("body").attr("class", "spawning");
                $("#edit").fadeOut();
                setHostName(response.host);
            }
        }
    );
});

var sortBy = function(field, reverse, primer){
    reverse = (reverse) ? -1 : 1;
    return function(a,b){
        a = a[field];
        b = b[field];
       if (typeof(primer) != 'undefined'){
           a = primer(a);
           b = primer(b);
       }
       if (a<b) return reverse * -1;
       if (a>b) return reverse * 1;
       return 0;
    }
}

// Sorting by column
var alternate = false; //used by jqote2.min.js
var sortAttribute = "name";
var workerSortAttribute = "id";
var desc = false;
var workerDesc = false;
var report;
var failuresSortAttribute = "name";
var failuresDesc = false;

function renderTable(report) {
    var totalRow = report.stats.pop();
    totalRow.is_aggregated = true;
    var sortedStats = (report.stats).sort(sortBy(sortAttribute, desc));
    sortedStats.push(totalRow);
    $('#stats tbody').empty();
    $('#errors tbody').empty();

    window.alternate = false;
    $('#stats tbody').jqoteapp(stats_tpl, sortedStats);

    window.alternate = false;
    $('#errors tbody').jqoteapp(errors_tpl, (report.errors).sort(sortBy(failuresSortAttribute, failuresDesc)));

    $("#total_rps").html(Math.round(report.total_rps*100)/100);
    $("#fail_ratio").html(Math.round(report.fail_ratio*100));
    $("#status_text").html(report.state);
    $("#userCount").html(report.user_count);
}

function renderWorkerTable(report) {
    if (report.workers) {
        var workers = (report.workers).sort(sortBy(workerSortAttribute, workerDesc));
        $("#workers tbody").empty();
        window.alternate = false;
        $("#workers tbody").jqoteapp(workers_tpl, workers);
        $("#workerCount").html(workers.length);
    }
}


$("#stats .stats_label").click(function(event) {
    event.preventDefault();
    sortAttribute = $(this).attr("data-sortkey");
    desc = !desc;
    renderTable(window.report);
});

$("#errors .stats_label").click(function(event) {
    event.preventDefault();
    failuresSortAttribute = $(this).attr("data-sortkey");
    failuresDesc = !failuresDesc;
    renderTable(window.report);
});

$("#workers .stats_label").click(function(event) {
    event.preventDefault();
    workerSortAttribute = $(this).attr("data-sortkey");
    workerDesc = !workerDesc;
    renderWorkerTable(window.report);
});

function update_stats_charts(){
    if(stats_history["time"].length > 0){
        rpsChart.chart.setOption({
            xAxis: {data: stats_history["time"]},
            series: [
                {data: stats_history["current_rps"]},
                {data: stats_history["current_fail_per_sec"]},
            ]
        });

        responseTimeChart.chart.setOption({
            xAxis: {data: stats_history["time"]},
            series: [
                {data: stats_history["response_time_percentile_50"]},
                {data: stats_history["response_time_percentile_95"]},
            ]
        });

        usersChart.chart.setOption({
            xAxis: {
                data: stats_history["time"]
            },
            series: [
                {data: stats_history["user_count"]},
            ]
        });
    }
}

// init charts
var rpsChart = new LocustLineChart($(".charts-container"), "Total Requests per Second", ["RPS", "Failures/s"], "reqs/s", ['#00ca5a', '#ff6d6d']);
var responseTimeChart = new LocustLineChart($(".charts-container"), "Response Times (ms)", ["Median Response Time", "95% percentile"], "ms");
var usersChart = new LocustLineChart($(".charts-container"), "Number of Users", ["Users"], "users");
charts.push(rpsChart, responseTimeChart, usersChart);
update_stats_charts()

function updateStats() {
    $.get('./stats/requests', function (report) {
        window.report = report;
        try{
            renderTable(report);
            renderWorkerTable(report);

            if (report.state !== "stopped"){
                // get total stats row
                var total = report.stats[report.stats.length-1];
                // update charts
                stats_history["time"].push(new Date().toLocaleTimeString());
                stats_history["user_count"].push({"value": report.user_count});
                stats_history["current_rps"].push({"value": total.current_rps, "users": report.user_count});
                stats_history["current_fail_per_sec"].push({"value": total.current_fail_per_sec, "users": report.user_count});
                stats_history["response_time_percentile_50"].push({"value": report.current_response_time_percentile_50, "users": report.user_count});
                stats_history["response_time_percentile_95"].push({"value": report.current_response_time_percentile_95, "users": report.user_count});
                update_stats_charts()
            } else {
                appearStopped();
            }
        } catch(i){
            console.debug(i);
        }
    }).always(function() {
        setTimeout(updateStats, 2000);
    });
}
updateStats();

function updateExceptions() {
    $.get('./exceptions', function (data) {
        $('#exceptions tbody').empty();
        $('#exceptions tbody').jqoteapp(exceptions_tpl, data.exceptions);
        setTimeout(updateExceptions, 5000);
    });
}
updateExceptions();
