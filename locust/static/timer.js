var sec = 0;
var clicked = false;

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
        setTimeout(updateTimer, 1000);
    });
}

updateTimer();

$(".stop-clock").click(function (event) {
    clicked = false;
});

$(".start-clock").click(function (event) {
    clicked = true;
    sec = 0;
});