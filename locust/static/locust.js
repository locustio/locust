$(window).ready(function() {
    $('.select2').select2({theme: 'bootstrap', width: "100%"});
    if($("#locust_count").length > 0) {
        $("#locust_count").focus().select();
    }
});

$("#locustfile").on('select2:close', function(event){
    event.preventDefault();
    var el = $(this);
    if(el.val()==="add_new_test_file") {
        $('#add-new-file-modal').modal('show'); 
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
    $(".edit").hide();
});

$("#box_stop a.reset-button").click(function(event) {
    event.preventDefault();
    $.get($(this).attr("href"));
});

$(".manual_ramp_link").click(function(event) {
    event.preventDefault();

    $("#ramp").hide();
    $("#start").show();
    $("#edit_config").hide();
    $("#locust_count").focus().select();
    $(".status").removeClass("none");
});

$(".ramp_test").click(function(event) {
    event.preventDefault();

    $("#start").hide();
    $("#ramp").show();
    $("#edit_config").hide();
    $("#init_count").focus().select();
    $(".status").removeClass("none");
});

$("#new_test").click(function(event) {
    event.preventDefault();
    $("#new-test-confirmation").modal('show');
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

var chartFilters = ['users','rps','response time','failures']
$(".chart-filter > button").click(function(event) {
    let activeFilters = advanceChart.getActiveFilter()
    if(!!advanceChart) {
        if(!activeFilters.includes($(this).index())) {
            if(activeFilters.length < 2) {
                advanceChart.addFilter($(this).index())
                $(this).removeClass("btn-outline-secondary")
                $(this).addClass("btn-secondary")
            }
        } else {
            if(activeFilters.length > 1) {
                advanceChart.removeFilter($(this).index())
                $(this).removeClass("btn-secondary")
                $(this).addClass("btn-outline-secondary")
            }
        }
    }
})

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
                resetCharts();
            }
        }
    );
});

$('.close_link_headers').click(function(event) {
    event.preventDefault();
    $("#column_name").empty();
    $(this).parent().parent().hide();
});

var alternate = false;

$("ul.tabs").tabs("div.panes > div").on("onClick", function(event) {
    if (event.target == $(".chart-tab-link")[0]) {
        // trigger resizing of charts
        if (!!rpsChart) rpsChart.resize()
        if (!!responseTimeChart) responseTimeChart.resize()
        if (!!usersChart) usersChart.resize()
        if (!!failureChart) failureChart.resize()
        if (!!advanceChart) advanceChart.resize()
        if (!!endpointResponseTimeCharts) {
          for (var chartKey in endpointResponseTimeCharts) {
            endpointResponseTimeCharts[chartKey].resize()
            endpointRpsCharts[chartKey].resize()
            endpointFailureCharts[chartKey].resize()
          }
        }
    }
});

$("ul.tabs_json").tabs("div.panes_json > div");


/*** START OF CONFIGURATION SECTION ***/

var simple_json_container = document.getElementById("json_editor");
var json_editor_options = {
    mode: 'tree',
    modes: ['code', 'tree'],
    onError: function (err) {
        alert(err.toString());
      }
}
var json_editor = new JSONEditor(simple_json_container, json_editor_options);
var old_config;

$(".edit_config_link").click(function(event) {
    event.preventDefault();
    try{
        $.ajax({
            type: "GET",
            url: "/config/get_config_content",
            success: function(response){
                old_config = JSON.parse(response.data)
                json_editor.set(old_config);
                $("#hidden_config_json").val(response.data);
                $("#start").hide();
                $("#ramp").hide();
                $("#edit_config").show();
                $(".status").addClass("none");
                $("#config_tab").trigger("click");
            }
        }); 
    }
    catch(err){
        alert("Failed to load configuration data.\n\nOriginal error message:\n" + err);
    }
    
});

$("#directories .select2").select2({
    placeholder: "Select a state"
});

let whichform = $('.upload_file_form_test_file')[0];

$('#upload_py_submit').click(function(event){
    event.preventDefault();
    whichform = $('.upload_file_form_test_file')[0];
    $('.upload_file_form_test_file').submit();
});

$('#upload_json_submit').click(function(event){
    event.preventDefault();
    whichform = $('.upload_file_form_json')[0];
    $('.upload_file_form_json').submit();
});

$('.upload_file_form_test_file, .upload_file_form_json').submit(function(event) {
    event.preventDefault();
    var form_data = new FormData(whichform);
    $.ajax({
        type: 'POST',
        url: "/upload_file",
        enctype: "multipart/form-data",
        contentType: false,
        data: form_data,
        cache: false,
        processData: false,
        success: function (response) {
            if (response.success) {
                location.reload(true);
            } else {
                alert(response.message);
            }
        }
    })
});

$('#submit_json_btn').click(function(){
    event.preventDefault();
    $('#hidden_config_json').val(JSON.stringify(json_editor.get(), null , 4));
    $('#json_config_form').submit();
});


$('#json_config_form').submit(function(event) {
    event.preventDefault();
    $.post($(this).attr("action"), $(this).serialize(),
        function(response) {
            if (response.success) {
                location.reload(true);
            }
        }
    );
});


$('#import_csv_btn').click(function(event) {
    event.preventDefault();
    var form = $('#import_csv_form')[0];
    var form_data = new FormData(form);
    $.ajax({
        type: 'POST',
        url: "/config/get_csv_column",
        enctype: 'multipart/form-data',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        success: function (response) {
            if (response.success) {
                $("#column_name").empty();
                $(".multiple_column").show();
                $(this).parent().remove();
                var rownum = 0;
                if(response.columns.length > 1)
                {
                    $.each(response.columns, function (key, value) {
                        rownum++;
                        var li = $('<li><span><input type="checkbox" id="headers_checkbox'+rownum+'" name="headers_checkbox" value="' + value + '"> '+value+'</span>');
                        $('#column_name').append(li);
                        $('#headers_checkbox'+rownum).on('click', function(){
                            if($(this).is(":checked")) {
                                $(this).prop("checked",true);
                            }
                            else {
                                $(this).prop("checked",false);
                            }
                        });

                    });
                    $("#column_name_container").show();
                }
                else{
                    $("#column_name_container").hide();
                }
            }
        }
    })
});

$('#multiple_column_form').submit(function(event) {
    event.preventDefault();
    $.post($(this).attr("action"), $(this).serialize(),
        function(response) {
            if (response.success) {
                location.reload(true);
            }
            else {
                alert("Convert error : " + response.message);
            }
        }
    );
});

$('#convert_csv_btn').click(function(){
    event.preventDefault();
    try{
        $("#multiple_hidden_config_json").val(JSON.stringify(json_editor.get(), null , 4));
        var form = $('#multiple_column_form')[0];
        var form_data = new FormData(form);
        $.ajax({
            type:'POST',
            url: '/config/convert_csv',
            enctype: 'multipart/form-data',
            data: form_data,
            cache: false,
            contentType: false,
            processData: false,
            success: function(response){
                if (response.success) {
                    try{
                        json_editor.set(JSON.parse(response.data));
                        $(".multiple_column").hide();
                        $("#column_name").empty();
                        document.getElementById("import_csv_form").reset();
                    }
                    catch(err){
                        alert(err.message);
                    }
                }
                else {
                    alert("Convert error : " + response.message);
                }
            }
        });
    }
    catch(err){
        alert("Something wrong with the data in editor. Please check it.\n\nOriginal error message:\n" + err);
    }
});

$(".config_new_test").click(function(event) {
    event.preventDefault();
    if(JSON.stringify(old_config,null,4) != JSON.stringify(json_editor.get(),null,4)) {
        $("#not_save_json_btn").attr("data-origin-link", "new test");
        $("#modal_confirm_save_json").modal();
    }
    else {
        $("#start").show();
        $("#ramp").hide();
        $("#edit_config").hide();
        $("#locust_count").focus().select();
        $(".status").removeClass("none");
    }
});

$(".config_ramp_test").click(function(event) {
    event.preventDefault();
    if(JSON.stringify(old_config,null,4) != JSON.stringify(json_editor.get(),null,4)) {
        $("#not_save_json_btn").attr("data-origin-link", "new ramp");
        $("#modal_confirm_save_json").modal();
    }
    else {
        $("#start").hide();
        $("#ramp").show();
        $("#edit_config").hide();
        $("#init_count").focus().select();
        $(".status").removeClass("none");
    }
});


$("#save_json_btn").click(function(event) {
    $("#submit_json_btn").trigger("click");
});

$("#not_save_json_btn").click(function(event) {
    $("#modal_confirm_save_json").modal("hide");
    if($("#not_save_json_btn").attr("data-origin-link") == "new test") {
        $("#start").show();
        $("#ramp").hide();
    }
    else if($("#not_save_json_btn").attr("data-origin-link") == "new ramp") {
        $("#ramp").show();
        $("#start").hide();
    }
    $("#edit_config").hide();
    $("#locust_count").focus().select();
    $(".status").removeClass("none");
});


/* END OF CONFIGURATION SECTION */

var stats_tpl = $('#stats-template');
var errors_tpl = $('#errors-template');
var exceptions_tpl = $('#exceptions-template');

$('#swarm_form').submit(function(event) {
    event.preventDefault();
    $.post($(this).attr("action"), $(this).serialize(),
        function(response) {
            if (response.success) {
                $("body").attr("class", "hatching");
                $("#start").hide();
                $("#status").show();
                $(".box_running").show();
                $("a.new_test").hide();
                $("a.edit_test").show();
                $(".user_count").show();
                $(".menu").show();
                $("#stats").show();
                $(".box_running").show();
                resetCharts();
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
var rpsChart, responseTimeChart, usersChart, failureChart, endpointResponseTimeCharts, endpointRpsCharts, endpointFailureCharts, advanceChart;
const totalKey = "total"

function updateStats() {
    $.get('/stats/requests', function (data) {
        report = JSON.parse(data);
        $("#total_rps").html(Math.round(report.total_rps*100)/100);
        $("#fail_ratio").html(Math.round(report.fail_ratio*100));
        $("#status_text").html(report.state);
        $("#userCount").html(report.user_count);
        $("#running_type").html(report.running_type);
        $("#host_url").html(report.host)

        if (typeof report.slave_count !== "undefined")
            $("#slaveCount").html(report.slave_count)

        RAMP = "Auto"
        if (report.running_type == RAMP) {
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
            let statsNoTotal = report.stats.splice(0,endpointChartSize)
            if(statsNoTotal.length > 1) {
              statsNoTotal = statsNoTotal.sort(function(a, b) {
                let keyA = a.name.toUpperCase() + a.method.toUpperCase(); // ignore upper and lowercase
                let keyB = b.name.toUpperCase() + b.method.toUpperCase(); // ignore upper and lowercase
                if (keyA < keyB) return -1;
                if (keyA > keyB) return 1;
                return 0;
              })
            }
            for (let i=0; i < statsNoTotal.length; i++) {
              chartKey = statsNoTotal[i].name.toUpperCase() + statsNoTotal[i].method.toUpperCase()
              createEndpointLines(chartKey, statsNoTotal[i].name, (chartKey) => {
                rpsValues.push(statsNoTotal[i].current_rps)
                responseTimeValues.push(statsNoTotal[i].avg_response_time)
                failureValues.push(statsNoTotal[i].num_failures)
              })
            }
            endpointResponseTimeCharts[totalKey].addValue([total.avg_response_time]);
            endpointRpsCharts[totalKey].addValue([total.current_rps]);
            endpointFailureCharts[totalKey].addValue([total.num_failures]);
            failureChart.addValue(failureValues);
            rpsChart.addValue(rpsValues);
            responseTimeChart.addValue(responseTimeValues);
            advanceChart.addValue([[report.user_count],rpsValues,responseTimeValues,failureValues])
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

function createEndpointLines(chartKey, name, callback) {
    if(!rpsChart.isLineExist(chartKey)) rpsChart.addLine(chartKey, name);
    if(!responseTimeChart.isLineExist(chartKey)) responseTimeChart.addLine(chartKey , name);
    if(!failureChart.isLineExist(chartKey)) failureChart.addLine(chartKey, name);
    if(!advanceChart.isLineExist(1,chartKey)) {
        for(let l=1; l < chartFilters.length; l++) {
            advanceChart.addLine(l,chartKey,name)
        }
    }
    callback(chartKey)
}

function resetCharts() {
  if (!!rpsChart) rpsChart.dispose()
  if (!!responseTimeChart) responseTimeChart.dispose()
  if (!!usersChart) usersChart.dispose()
  if (!!failureChart) failureChart.dispose()
  if (!!advanceChart) advanceChart.dispose()
  if (!!endpointResponseTimeCharts) {
    for (var chartKey in endpointResponseTimeCharts) {
      endpointResponseTimeCharts[chartKey].dispose()
      endpointRpsCharts[chartKey].dispose()
      endpointFailureCharts[chartKey].dispose()
    }
  }
  $('.charts-container').empty()
  advanceChart = new LocustAdvanceLineChart($(".charts-container"), "Advance Chart", "", chartFilters, ['users','reqs/s','ms','failures'], "100%");
  rpsChart = new LocustLineChart($(".charts-container"), "Requests per Second", "", [], "reqs/s", "100%");
  responseTimeChart = new LocustLineChart($(".charts-container"), "Average Response Time", "", [], "ms", "100%");
  usersChart = new LocustLineChart($(".charts-container"), "Number of Users", "", ["Total"], "users", "100%");
  failureChart = new LocustLineChart($(".charts-container"), "Number of Failures", "", [], "failures", "100%");
  advanceChart.addLine(0,"Total","Total")
  $(".chart-filter > button")[chartFilters.indexOf('response time')].click()
  endpointResponseTimeCharts = []
  endpointRpsCharts = []
  endpointFailureCharts = []
  initTotalCharts()
}
resetCharts()

function initTotalCharts() {
  endpointResponseTimeCharts[totalKey] = new LocustLineChart($(".charts-container"), "Average Responses Time", totalKey.toUpperCase(), ["Average Responses Time"], "ms", "33.3%");
  endpointRpsCharts[totalKey] = new LocustLineChart($(".charts-container"), "Requests Per Second", totalKey.toUpperCase(), ["RPS"], "request", "33.3%");
  endpointFailureCharts[totalKey] = new LocustLineChart($(".charts-container"), "Failure", totalKey.toUpperCase(), ["Failures"], "failure", "33.3%");
}