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
});

$("#new_test").click(function(event) {
    event.preventDefault();
    $("#start").show();
    $("#locust_count").focus().select();
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
var errors_tpl = $('#errors-template');
var exceptions_tpl = $('#exceptions-template');
var slaves_tpl = $('#slave-template');

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
var slaveSortAttribute = "id";
var desc = false;
var report;
$(".stats_label").click(function(event) {
    event.preventDefault();
    sortAttribute = $(this).attr("data-sortkey");
    desc = !desc;

    $('#stats tbody').empty();
    $('#errors tbody').empty();
    alternate = false;
    totalRow = report.stats.pop();
    sortedStats = (report.stats).sort(sortBy(sortAttribute, desc));
    sortedStats.push(totalRow);
    $('#stats tbody').jqoteapp(stats_tpl, sortedStats);
    alternate = false;
    $('#errors tbody').jqoteapp(errors_tpl, (report.errors).sort(sortBy(sortAttribute, desc)));
});

// init charts
var rpsChart = new LocustLineChart($(".charts-container"), "Total Requests per Second", ["RPS"], "reqs/s");
var responseTimeChart = new LocustLineChart($(".charts-container"), "Response Times (ms)", ["Median Response Time", "95% percentile"], "ms");
var usersChart = new LocustLineChart($(".charts-container"), "Number of Users", ["Users"], "users");

function updateStats() {
    $.get('./stats/requests', function (report) {
        $("#total_rps").html(Math.round(report.total_rps*100)/100);
        //$("#fail_ratio").html(Math.round(report.fail_ratio*10000)/100);
        $("#fail_ratio").html(Math.round(report.fail_ratio*100));
        $("#status_text").html(report.state);
        $("#userCount").html(report.user_count);

        if (report.slaves) {
            slaves = (report.slaves).sort(sortBy(slaveSortAttribute, desc));
            $("#slaves tbody").empty();
            $("#slaves tbody").jqoteapp(slaves_tpl, slaves);
            $("#slaveCount").html(slaves.length);
        }

        $('#stats tbody').empty();
        $('#errors tbody').empty();

        alternate = false;

        totalRow = report.stats.pop();
        sortedStats = (report.stats).sort(sortBy(sortAttribute, desc));
        sortedStats.push(totalRow);
        $('#stats tbody').jqoteapp(stats_tpl, sortedStats);
        alternate = false;
        $('#errors tbody').jqoteapp(errors_tpl, (report.errors).sort(sortBy(sortAttribute, desc)));

        if (report.state !== "stopped"){
            // get total stats row
            var total = report.stats[report.stats.length-1];
            // update charts
            rpsChart.addValue([total.current_rps]);
            responseTimeChart.addValue([report.current_response_time_percentile_50, report.current_response_time_percentile_95]);
            usersChart.addValue([report.user_count]);
        }

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
