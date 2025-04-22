import os
from html import escape
from itertools import chain

from jinja2 import Environment as JinjaEnvironment
from jinja2 import FileSystemLoader

from . import stats
from .runners import STATE_STOPPED, STATE_STOPPING, MasterRunner
from .user.inspectuser import get_ratio
from .util.date import format_duration, format_utc_timestamp

PERCENTILES_FOR_HTML_REPORT = [0.50, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
DEFAULT_BUILD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webui", "dist")


def process_html_filename(options) -> None:
    option_mapping = {
        "{u}": options.num_users,
        "{r}": options.spawn_rate,
        "{t}": options.run_time,
    }
    for option_term, option_value in option_mapping.items():
        if option_value is not None:
            options.html_file = options.html_file.replace(option_term, str(int(option_value)))


def render_template_from(file, build_path=DEFAULT_BUILD_PATH, **kwargs):
    env = JinjaEnvironment(loader=FileSystemLoader(build_path))
    template = env.get_template(file)
    return template.render(**kwargs)


def get_html_report(
    environment,
    show_download_link=True,
    theme="",
):
    request_stats = environment.runner.stats

    start_time = format_utc_timestamp(request_stats.start_time)

    if end_ts := request_stats.last_request_timestamp:
        end_time = format_utc_timestamp(end_ts)
    else:
        end_ts = request_stats.start_time
        end_time = start_time

    host = None
    if environment.host:
        host = environment.host
    elif environment.runner.user_classes:
        all_hosts = {l.host for l in environment.runner.user_classes}
        if len(all_hosts) == 1:
            host = list(all_hosts)[0]

    requests_statistics = list(chain(stats.sort_stats(request_stats.entries), [request_stats.total]))
    failures_statistics = stats.sort_stats(request_stats.errors)
    exceptions_statistics = [
        {**exc, "nodes": ", ".join(exc["nodes"])} for exc in environment.runner.exceptions.values()
    ]

    if request_stats.history and request_stats.history[-1]["time"] < end_time:
        stats.update_stats_history(environment.runner, end_time)
    history = request_stats.history

    is_distributed = isinstance(environment.runner, MasterRunner)
    user_spawned = (
        environment.runner.reported_user_classes_count if is_distributed else environment.runner.user_classes_count
    )

    if environment.runner.state in [STATE_STOPPED, STATE_STOPPING]:
        user_spawned = environment.runner.final_user_classes_count

    task_data = {
        "per_class": get_ratio(environment.user_classes, user_spawned, False),
        "total": get_ratio(environment.user_classes, user_spawned, True),
    }

    return render_template_from(
        "report.html",
        template_args={
            "is_report": True,
            "requests_statistics": [stat.to_dict(escape_string_values=True) for stat in requests_statistics],
            "failures_statistics": [stat.to_dict() for stat in failures_statistics],
            "exceptions_statistics": [stat for stat in exceptions_statistics],
            "response_time_statistics": [
                {
                    "name": escape(stat.name),
                    "method": escape(stat.method or ""),
                    **{
                        str(percentile): stat.get_response_time_percentile(percentile)
                        for percentile in PERCENTILES_FOR_HTML_REPORT
                    },
                }
                for stat in requests_statistics
            ],
            "start_time": start_time,
            "end_time": end_time,
            "duration": format_duration(request_stats.start_time, end_ts),
            "host": escape(str(host)),
            "history": history,
            "show_download_link": show_download_link,
            "locustfile": escape(str(environment.locustfile)),
            "tasks": task_data,
            "percentiles_to_chart": stats.PERCENTILES_TO_CHART,
            "profile": escape(str(environment.profile)) if environment.profile else None,
        },
        theme=theme,
    )
