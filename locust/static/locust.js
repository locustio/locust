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
var rpsChart = new LocustLineChart($(".charts-container"), "Total Requests per Second", "", ["Total"], "reqs/s", "100%");
var responseTimeChart = new LocustLineChart($(".charts-container"), "Average Response Time", "", ["Total Average"], "ms", "100%");
var usersChart = new LocustLineChart($(".charts-container"), "Number of Users", "", ["Total"], "users", "100%");
var failureChart = new LocustLineChart($(".charts-container"), "Number of Failures", "", ["Total"], "failures", "100%");
var endpointResponseTimeCharts = []
var endpointRpsCharts = []
var endpointFailureCharts = []

function updateStats() {
    $.get('/stats/requests', function (data) {
        report = JSON.parse(data);
        $("#total_rps").html(Math.round(report.total_rps*100)/100);
        $("#fail_ratio").html(Math.round(report.fail_ratio*100));
        $("#status_text").html(report.state);
        $("#userCount").html(report.user_count);

        if (typeof report.slave_count !== "undefined")
            $("#slaveCount").html(report.slave_count)

        $('#stats tbody').empty();
        $('#errors tbody').empty();

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
            rpsValues = [total.current_rps]
            responseTimeValues = [total.avg_response_time]
            failureValues = [total.num_failures]

            for(i=0; i< endpointChartSize; i++) {
              chartKey = report.stats[i].name
              createEndpointCharts(chartKey, (chartKey) => {
                endpointResponseTimeCharts[chartKey].addValue([report.stats[i].avg_response_time]);
                endpointRpsCharts[chartKey].addValue([report.stats[i].current_rps]);
                endpointFailureCharts[chartKey].addValue([report.stats[i].num_failures]);
              })
              rpsValues.push(report.stats[i].current_rps)
              responseTimeValues.push(report.stats[i].avg_response_time)
              failureValues.push(report.stats[i].num_failures)
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

function createEndpointCharts(chartKey, callback) {
  if(!endpointResponseTimeCharts[chartKey]) {
    title = "Average Response Times"
    endpointResponseTimeCharts[chartKey] = new LocustLineChart($(".charts-container"), title, chartKey, ["Average Response Time"], "ms", "33%");
    endpointResponseTimeCharts[chartKey].resize()
  }
  if(!endpointRpsCharts[chartKey]) {
    title = "Requests per Second"
    endpointRpsCharts[chartKey] = new LocustLineChart($(".charts-container"), title, chartKey, ["RPS"], "request", "33%");
    endpointRpsCharts[chartKey].resize()
  }
  if(!endpointFailureCharts[chartKey]) {
    title = "Failures"
    endpointFailureCharts[chartKey] = new LocustLineChart($(".charts-container"), title, chartKey, ["Failure"], "failure", "33%");
    endpointFailureCharts[chartKey].resize()
  }
  if(!rpsChart.isLineExist(chartKey)) rpsChart.addLine(chartKey);
  if(!responseTimeChart.isLineExist(chartKey)) responseTimeChart.addLine(chartKey);
  if(!failureChart.isLineExist(chartKey)) failureChart.addLine(chartKey);

  callback(chartKey)
}
