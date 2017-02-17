$(window).ready(function() {
    if($("#locust_count").length > 0) {
        $("#locust_count").focus().select();
    }
});

$("#box_stop a").click(function(event) {
    event.preventDefault();
    $.get($(this).attr("href"));
    $("body").attr("class", "stopped");
    $(".box_stop").hide();
    $("a.new_test").show();
    $("a.edit_test").hide();
    $(".user_count").hide();
});

$("#box_reset a").click(function(event) {
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

$("ul.tabs").tabs("div.panes > div");

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


var charts = {}

function initChart(stat) {
    var width = $(".main").width();
    var rps_element = $('<div class="chart"></div>').css("width", width);
    var avt_element = $('<div class="chart"></div>').css("width", width);
    rps_element.appendTo("#charts .charts-container");
    avt_element.appendTo("#charts .charts-container");

    var date = [];
    var rps_data = [];
    var avt_data = [];

    now = new Date().toLocaleTimeString();
    date.push(now);
    rps_data.push({
        "name": now,
        "value": Math.round(stat.current_rps*100)/100
    });

    avt_data.push({
        "name": now,
        "value": Math.round(stat.avg_response_time)
    });
    
    var gridSettings = {x:60, y:70, x2:40, y2:40};

    var rps_chart = echarts.init(rps_element.get(0), 'vintage');
    rps_chart.setOption({
        title: {
            text: 'Total Requests per Second',
            x: 10,
            y: 10,
        },
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                param = params[0];
                return param.name + ': ' + param.value + ' reqs/s';
            },
            axisPointer: {
                animation: true
            }
        },
        xAxis: {
            type: 'category',
            splitLine: {
                show: false
            },
            data: date
        },
        yAxis: {
            type: 'value',
            boundaryGap: [0, '100%'],
            splitLine: {
                show: false
            }
        },
        series: [{
            name: 'RPS',
            type: 'line',
            showSymbol: false,
            hoverAnimation: false,
            data: rps_data
        }],
        grid: gridSettings,
    });

    var avt_chart = echarts.init(avt_element.get(0), 'vintage');
    avt_chart.setOption({
        title: {
            text: 'Average Response Time',
            x: 10,
            y: 10,
        },
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                param = params[0];
                return param.name + ': ' + param.value + 'ms';
            },
            axisPointer: {
                animation: true
            }
        },
        xAxis: {
            type: 'category',
            splitLine: {
                show: false
            },
            data: date
        },
        yAxis: {
            type: 'value',
            boundaryGap: [0, '100%'],
            splitLine: {
                show: false
            }
        },
        series: [{
            name: 'AVT',
            type: 'line',
            showSymbol: false,
            hoverAnimation: false,
            data: avt_data
        }],
        grid: gridSettings,
    });

    charts[stat.name] = {};
    charts[stat.name]["date"] = date;
    charts[stat.name]["rps_chart"] = rps_chart;
    charts[stat.name]["rps_data"] = rps_data;
    charts[stat.name]["avt_chart"] = avt_chart;
    charts[stat.name]["avt_data"] = avt_data;

}

function updateCharts(stats) {
    var rps_chart, rps_data, now, date, avt_chart, avt_data;
    
    $.each(stats, function(index, stat){
        if (stat.name != "Total") {
            // Only render charts for the total data
            return;
        }
        if (stat.name in charts) {
            now = new Date().toLocaleTimeString();
            date = charts[stat.name]["date"];
            date.push(now);

            rps_chart = charts[stat.name]["rps_chart"];
            rps_data = charts[stat.name]["rps_data"];
            rps_data.push({
                "name": now,
                "value": Math.round(stat.current_rps*100)/100
            });
            rps_chart.setOption({
                xAxis: {
                    data: date
                },
                series: [{
                    data: rps_data
                }]
            });

            avt_chart = charts[stat.name]["avt_chart"];
            avt_data = charts[stat.name]["avt_data"];
            avt_data.push({
                "name": now,
                "value": Math.round(stat.avg_response_time)
            });

            avt_chart.setOption({
                xAxis: {
                    data: date
                },
                series: [{
                    data: avt_data
                }]
            });
        } else {
            initChart(stat);
        }
    });
}


function updateStats() {
    $.get('/stats/requests', function (data) {
        report = JSON.parse(data);
        $("#total_rps").html(Math.round(report.total_rps*100)/100);
        //$("#fail_ratio").html(Math.round(report.fail_ratio*10000)/100);
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
            updateCharts(sortedStats);
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
