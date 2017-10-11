var sec = 0;
var clicked = false;

$(".stop-clock").click(function (event) {
    clicked = false;
});

$(".start-clock").click(function (event) {
    clicked = true;
    sec = 0;
});

function updateTimer() {
    $.get('/stats/requests', function (data) {
        report = JSON.parse(data);
        var time;
        var totalRunTimeInSeconds = report.total_run_time;

        if (totalRunTimeInSeconds >= sec) {
            time = totalRunTimeInSeconds;
        } else {
            time = sec;
        }
        $("#run_time").html(String(time).toHHMMSS());
        if (clicked) {
            sec++;
        }

    });
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
