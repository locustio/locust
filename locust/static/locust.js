$(window).ready(function() {
    if($("#locust_count").length > 0) {
        $("#locust_count").focus().select();
    }
});

$("#box_stop a.stop-button").click(function(event) {
    event.preventDefault();
    $.get($(this).attr("href"));
    $("body").attr("class", "stopped");
    $(".box_stop").hide();
    $("a.new_test").show();
    $("a.edit_test").hide();
    $(".user_count").hide();
});

$("#box_stop a.reset-button").click(function(event) {
    event.preventDefault();
    $.get($(this).attr("href"));
    rpsChart.reset();
    responseTimeChart.reset();
    usersChart.reset();
});

$("#new_test").click(function(event) {
    event.preventDefault();
    $("#start").show();
    $("#locust_count").focus().select();
});

$("#new_target").click(function(event) {
    event.preventDefault();
    $("#config").show();
    $("#host_url").focus().select();
});

$(".edit_test").click(function(event) {
    event.preventDefault();
    $("#edit").show();
    $("#new_locust_count").focus().select();
});

$(".close_link").click(function(event) {
    event.preventDefault();
    $(this).parent().parent().hide();
});

var alternate = false;

$("ul.tabs").tabs("div.panes > div").on("onClick", function(event) {
    if (event.target == $(".chart-tab-link")[0]) {
        // trigger resizing of charts
        rpsChart.resize();
        responseTimeChart.resize();
        usersChart.resize();
    }
});

var stats_tpl = $('#stats-template');
var task_stats_tpl = $('#task-stats-template');
var errors_tpl = $('#errors-template');
var task_errors_tpl = $('#task-errors-template')
var exceptions_tpl = $('#exceptions-template');

$('#swarm_form').submit(function(event) {
    event.preventDefault();
    $.post($(this).attr("action"), $(this).serialize(),
        function(response) {
            if (response.success) {
                $("body").attr("class", "hatching");
                $("#start").fadeOut();
                $("#status").fadeIn();
                $(".box_running").fadeIn();
                $("a.new_test").fadeOut();
                $("a.edit_test").fadeIn();
                $(".user_count").fadeIn();
            }
        }
    );
});

$('#edit_form').submit(function(event) {
    event.preventDefault();
    $.post($(this).attr("action"), $(this).serialize(),
        function(response) {
            if (response.success) {
                $("body").attr("class", "hatching");
                $("#edit").fadeOut();
            }
        }
    );
});

$('#config_form').submit(function(event) {
    event.preventDefault();
    $.post($(this).attr("action"), $(this).serialize(),
        function(response) {
            if (response.success) {
                $("#host_url").html(response.new_host);
                $("#config").fadeOut();
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
var sortAttribute = "name";
var altSortAttribute = "task";
var desc = false;
var report;
$(".stats_label").click(function(event) {
    event.preventDefault();
    sortAttribute = $(this).attr("data-sortkey");
    desc = !desc;

    $('#stats tbody').empty();
    $('#errors tbody').empty();
    alternate = false;
    totalRow = report.stats.pop()
    sortedStats = (report.stats).sort(sortBy(sortAttribute, desc))
    sortedStats.push(totalRow)
    $('#stats tbody').jqoteapp(stats_tpl, sortedStats);
    alternate = false;
    $('#errors tbody').jqoteapp(errors_tpl, (report.errors).sort(sortBy(sortAttribute, desc)));
});

$(".alt_stats_label").click(function(event) {
    event.preventDefault();
    sortAttribute = $(this).attr("data-sortkey");
    desc = !desc;

    $('#taskStats tbody').empty();
    $('#taskErrors tbody').empty();
    alternate = false;
    totalStatsRow = report.taskStats.pop();
    sortedTaskStats = (report.taskStats).sort(sortBy(altSortAttribute, desc));
    sortedTaskStats.push(totalStatsRow);
    $('#taskStats tbody').jqoteapp(task_stats_tpl, sortedTaskStats);
    alternate = false;
    $('#taskErrors tbody').jqoteapp(
        task_errors_tpl, 
        (report.tasksFailures).sort(sortBy(altSortAttribute, desc))
    );
});

// init charts
var rpsChart = new LocustLineChart($(".charts-container"), "Total Requests per Second", ["Total"], "reqs/s");
var responseTimeChart = new LocustLineChart($(".charts-container"), "Average Response Time", ["Total"], "ms");
var usersChart = new LocustLineChart($(".charts-container"), "Number of Users", ["Users"], "users");

function updateStats() {
    $.get('/stats/requests', function (data) {
        report = JSON.parse(data);
        $("#total_rps").html(Math.round(report.total_rps*100)/100);
        //$("#fail_ratio").html(Math.round(report.fail_ratio*10000)/100);
        $("#fail_ratio").html(Math.round(report.fail_ratio*100));
        $("#status_text").html(report.state);
        $("#userCount").html(report.user_count);

        $("#slaveCount").html(report.slave_count)
        $("#workerCount").html(report.worker_count)

        $('#stats tbody').empty();
        $('#errors tbody').empty();

        $('#taskStats tbody').empty();
        $('#taskErrors tbody').empty();

        alternate = false;

        totalRow = report.stats.pop();
        sortedStats = (report.stats).sort(sortBy(sortAttribute, desc));
        sortedStats.push(totalRow);
        $('#stats tbody').jqoteapp(stats_tpl, sortedStats);
        alternate = false;
        $('#errors tbody').jqoteapp(errors_tpl, (report.errors).sort(sortBy(sortAttribute, desc)));
        
        totalStatsRow = report.taskStats.pop();
        sortedTaskStats = (report.taskStats).sort(sortBy(altSortAttribute, desc));
        sortedTaskStats.push(totalStatsRow);
        $('#taskStats tbody').jqoteapp(task_stats_tpl, sortedTaskStats);
        alternate = false;
        $('#taskErrors tbody').jqoteapp(
            task_errors_tpl, 
            (report.tasksFailures).sort(sortBy(altSortAttribute, desc))
        );

        if (report.state !== "stopped"){
            // update charts
            rps = report.stats
                .filter(function(x) { return x.task == "Action Total" || x.name == "Total" })
                .map(function(x) {
                return x.name == "Total" ? 
                    {name: "Total", value: x.current_rps} : 
                    {name: `${x.method} ${x.name}`, value: x.current_rps}
            });
            responseTime = report.stats
                .filter(function(x) { return x.task == "Action Total" || x.name == "Total" })
                .map(function(x) {
                return x.name == "Total" ? 
                    {name: "Total", value: x.avg_response_time} : 
                    {name: `${x.method} ${x.name}`, value: x.avg_response_time}
            });
            
            rpsChart.addValue(rps);
            responseTimeChart.addValue(responseTime);
            usersChart.addValue([{name: "Users", value: report.user_count}]);
        }

        setTimeout(updateStats, 2000);
    });
}
updateStats();

function updateExceptions() {
    $.get('/exceptions', function (data) {
        $('#exceptions tbody').empty();
        $('#exceptions tbody').jqoteapp(exceptions_tpl, data.exceptions);
        setTimeout(updateExceptions, 5000);
    });
}
updateExceptions();
