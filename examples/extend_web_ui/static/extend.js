var contentLengthStats;
var contentLengthCharts = {};

// Used for sorting
var contentLengthDesc = false;
var contentLengthSortAttribute = "name";

// Trigger sorting of stats when a table label is clicked
$("#content-length .stats_label").click(function (event) {
    event.preventDefault();
    contentLengthSortAttribute = $(this).attr("data-sortkey");
    contentLengthDesc = !contentLengthDesc;
    renderContentLengthTable(window.content_length_report);
});

// Render and sort Content Length table
function renderContentLengthTable(content_length_report) {
    $('#content-length tbody').empty();

    window.alternate = false;
    $('#content-length tbody').jqoteapp($('#content-length-template'), (content_length_report.stats).sort(sortBy(contentLengthSortAttribute, contentLengthDesc)));
}

// Get and repeatedly update Content Length stats and table
function updateContentLengthStats() {
    $.get('./content-length', function (content_length_report) {
        window.content_length_report = content_length_report
        $('#content-length tbody').empty();

        if (JSON.stringify(content_length_report) !== JSON.stringify({})) {
            renderContentLengthTable(content_length_report);

            // Make a separate chart for each URL
            for (let index = 0; index < content_length_report.stats.length; index++) {
                const url_stats = content_length_report.stats[index];

                // If a chart already exists, just add the new value
                if (contentLengthCharts.hasOwnProperty(url_stats.safe_name)) {
                    contentLengthCharts[url_stats.safe_name].addValue([url_stats.content_length]);
                } else {
                    // If a chart doesn't already exist, create the chart first then add the value
                    contentLengthCharts[url_stats.safe_name] = new LocustLineChart($(".content-length-chart-container"), `Content Length for ${url_stats.safe_name}`, ["content-length"], "bytes");
                    // Add newly created chart to Locust web UI's array of charts
                    charts.push(contentLengthCharts[url_stats.safe_name])
                    contentLengthCharts[url_stats.safe_name].addValue([url_stats.content_length]);
                }
            }
        }
        // Schedule a repeat of updating stats in 2 seconds
        setTimeout(updateContentLengthStats, 2000);
    });
}

updateContentLengthStats();
