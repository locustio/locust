var runTime = 0;
var isTestRunning = false;

$(".stop-timer").click(function (event) {
  isTestRunning = false;
});

$(".start-timer").click(function (event) {
  runTime = 0;
});

function updateTimer() {
    if ( runTime == 0 ) {
      $.get('/stats/requests', function (data) {
          report = JSON.parse(data);
          runTime = report.total_run_time;
          isTestRunning = (report.state == "stopped") ? false : true;
          //update the UI of timer to the last/current runtime
          $("#run_time").html(String(runTime).toHHMMSS())
          if (isTestRunning) ++runTime
          else runTime = 0
      })
    } else if (isTestRunning) {
      $("#run_time").html(String(runTime++).toHHMMSS());
    }
}
setInterval(updateTimer, 1000);

String.prototype.toHHMMSS = function () {
    var sec_num = parseInt(this, 10);
    var hours = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours < 10) {
        hours = "0" + hours;
    }
    if (minutes < 10) {
        minutes = "0" + minutes;
    }
    if (seconds < 10) {
        seconds = "0" + seconds;
    }
    var time = hours + ':' + minutes + ':' + seconds;
    return time;
};
