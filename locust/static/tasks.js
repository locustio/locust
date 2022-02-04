function getRatioPercent(ratio) {
    return (ratio * 100).toFixed(1) + "%";
}

function _initTasks_sub(li, tasks) {
    if (tasks) {
        var ul = $('<ul></ul>');
        for (const [key, task] of Object.entries(tasks)) {
            var liTask = $('<li></li>').text(getRatioPercent(task.ratio) + " " + key);
            _initTasks_sub(liTask, task.tasks);
            ul.append(liTask);
        }
        li.append(ul);
    }
}

function _getTasks_div(root, title) {
    var taskDiv = $('<div></div>');
    var taskDivHeading = $('<h3></h3>').text(title);
    taskDiv.append(taskDivHeading);
    var ulClasses = $('<ul></ul>');
    for (const [key, clazz] of Object.entries(root)) {
        var liClass = $('<li></li>').text(getRatioPercent(clazz.ratio) + " " + key);
        _initTasks_sub(liClass, clazz.tasks)
        ulClasses.append(liClass);
    }
    taskDiv.append(ulClasses);
    return taskDiv
}

function renderTasks(data) {
    var tasks = $('#tasks .tasks');
    tasks.empty();
    tasks.append(_getTasks_div(data.per_class, 'Ratio per User class'));
    tasks.append(_getTasks_div(data.total, 'Total ratio'));
}

function updateTasks() {
    $.get('/tasks', function (data) {
        renderTasks(data);
    }).fail(function() {
        // fallback issue #1994
        renderTasks($('#tasks .tasks').data('tasks'));
    });
}
updateTasks();
