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

$(".ramp_test").click(function(event) {
    event.preventDefault();
    $("#start").hide();
    $("#ramp").show();
});

$("#new_test").click(function(event) {
    event.preventDefault();
    $("#ramp").hide();
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

$('#ramp_form').submit(function(event) {
    event.preventDefault();
    $.post($(this).attr("action"), $(this).serialize(),
        function(response) {
            if (response.success) {
                $("body").attr("class", "hatching");
                $("#ramp").fadeOut();
                $("#status").fadeIn();
                $(".box_running").fadeIn();
                $("a.new_test").fadeOut();
                $("a.edit_test").fadeIn();
                $(".user_count").fadeIn();
            }
        }
    );
});

var alternate = false;

$("ul.tabs").tabs("div.panes > div").on("onClick", function(event) {
    if (event.target == $(".chart-tab-link")[0]) {
        // trigger resizing of charts
        rpsChart.resize();
        responseTimeChart.resize();
        usersChart.resize();
        failureChart.resize();
        for (var chartKey in endpointResponseTimeCharts) {
          endpointResponseTimeCharts[chartKey].resize();
          endpointRpsCharts[chartKey].resize();
          endpointFailureCharts[chartKey].resize();
        }
    }
});

var stats_tpl = $('#stats-template');
var errors_tpl = $('#errors-template');
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

// init charts
var rpsChart = new LocustLineChart($(".charts-container"), "Requests per Second", "", [], "reqs/s", "100%");
var responseTimeChart = new LocustLineChart($(".charts-container"), "Average Response Time", "", [], "ms", "100%");
var usersChart = new LocustLineChart($(".charts-container"), "Number of Users", "", ["Total"], "users", "100%");
var failureChart = new LocustLineChart($(".charts-container"), "Number of Failures", "", [], "failures", "100%");
var endpointResponseTimeCharts = []
var endpointRpsCharts = []
var endpointFailureCharts = []
const totalKey = "total"
initTotalCharts()

function updateStats() {
    $.get('/stats/requests', function (data) {
        report = JSON.parse(data);
        $("#total_rps").html(Math.round(report.total_rps*100)/100);
        $("#fail_ratio").html(Math.round(report.fail_ratio*100));
        $("#status_text").html(report.state);
        $("#userCount").html(report.user_count);
        $("#running_type").html(report.running_type);

        if (typeof report.slave_count !== "undefined")
            $("#slaveCount").html(report.slave_count)

        if (report.running_type == "auto") {
            $(".edit_test").addClass("none")
        } else {
            $(".edit_test").removeClass("none")
        }

        $('#stats tbody').empty();
        $('#errors tbody').empty();

        //Handle if user request to reset stats
        if(report.total_run_time < runTime ) {
          runTime = report.total_run_time;
          $("#run_time").html(String(runTime).toHHMMSS())
        }

        alternate = false;

        totalRow = report.stats.pop()
        sortedStats = (report.stats).sort(sortBy(sortAttribute, desc))
        sortedStats.push(totalRow)
        $('#stats tbody').jqoteapp(stats_tpl, sortedStats);
        alternate = false;
        $('#errors tbody').jqoteapp(errors_tpl, (report.errors).sort(sortBy(sortAttribute, desc)));

        if (report.state !== "stopped"){
            // get total stats row
            var total = report.stats[report.stats.length-1];

            endpointChartSize = report.stats.length - 1
            rpsValues = []
            responseTimeValues = []
            failureValues = []

            for (let i=0; i < report.stats.length; i++) {
              chartKey = report.stats[i].name
              if (total != report.stats[i]) {
                chartKey = chartKey + i
                createEndpointLines(chartKey, report.stats[i].name, (chartKey) => {
                  rpsValues.push(report.stats[i].current_rps)
                  responseTimeValues.push(report.stats[i].avg_response_time)
                  failureValues.push(report.stats[i].num_failures)
                })
              } else {
                endpointResponseTimeCharts[totalKey].addValue([report.stats[i].avg_response_time]);
                endpointRpsCharts[totalKey].addValue([report.stats[i].current_rps]);
                endpointFailureCharts[totalKey].addValue([report.stats[i].num_failures]);
              }
            }
            failureChart.addValue(failureValues);
            rpsChart.addValue(rpsValues);
            responseTimeChart.addValue(responseTimeValues);
            usersChart.addValue([report.user_count]);
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

function createEndpointLines(chartKey, endpointName, callback) {
    if(!rpsChart.isLineExist(chartKey)) rpsChart.addLine(chartKey, endpointName);
    if(!responseTimeChart.isLineExist(chartKey)) responseTimeChart.addLine(chartKey, endpointName);
    if(!failureChart.isLineExist(chartKey)) failureChart.addLine(chartKey, endpointName);
    callback(chartKey)
}

function initTotalCharts() {
  endpointResponseTimeCharts[totalKey] = new LocustLineChart($(".charts-container"), "Average Responses Time", totalKey.toUpperCase(), ["Average Responses Time"], "ms", "33.3%");
  endpointRpsCharts[totalKey] = new LocustLineChart($(".charts-container"), "Requests Per Second", totalKey.toUpperCase(), ["RPS"], "request", "33.3%");
  endpointFailureCharts[totalKey] = new LocustLineChart($(".charts-container"), "Failure", totalKey.toUpperCase(), ["Failures"], "failure", "33.3%");
}
