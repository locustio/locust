import glob
import os
import pathlib
from html import escape
from itertools import chain
from json import dumps

from jinja2 import Environment, FileSystemLoader

from . import stats as stats_module
from .runners import STATE_STOPPED, STATE_STOPPING, MasterRunner
from .stats import sort_stats, update_stats_history
from .user.inspectuser import get_ratio
from .util.date import format_utc_timestamp

PERCENTILES_FOR_HTML_REPORT = [0.50, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
BUILD_PATH = os.path.join(ROOT_PATH, "webui", "dist")
STATIC_PATH = os.path.join(BUILD_PATH, "assets")


def render_template(file, **kwargs):
    env = Environment(loader=FileSystemLoader(BUILD_PATH), extensions=["jinja2.ext.do"])
    template = env.get_template(file)
    return template.render(**kwargs)


def get_html_report(
    environment,
    show_download_link=True,
    theme="",
):
    stats = environment.runner.stats

    start_time = format_utc_timestamp(stats.start_time)

    if end_ts := stats.last_request_timestamp:
        end_time = format_utc_timestamp(end_ts)
    else:
        end_time = start_time

    host = None
    if environment.host:
        host = environment.host
    elif environment.runner.user_classes:
        all_hosts = {l.host for l in environment.runner.user_classes}
        if len(all_hosts) == 1:
            host = list(all_hosts)[0]

    requests_statistics = list(chain(sort_stats(stats.entries), [stats.total]))
    failures_statistics = sort_stats(stats.errors)
    exceptions_statistics = [
        {**exc, "nodes": ", ".join(exc["nodes"])} for exc in environment.runner.exceptions.values()
    ]

    update_stats_history(environment.runner)
    history = stats.history

    static_js = []
    js_files = [os.path.basename(filepath) for filepath in glob.glob(os.path.join(STATIC_PATH, "*.js"))]

    for js_file in js_files:
        path = os.path.join(STATIC_PATH, js_file)
        static_js.append("// " + js_file + "\n")
        with open(path, encoding="utf8") as f:
            static_js.append(f.read())
        static_js.extend(["", ""])

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

    return render_template(
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
            "host": escape(str(host)),
            "history": history,
            "show_download_link": show_download_link,
            "locustfile": escape(str(environment.locustfile)),
            "tasks": task_data,
            "percentiles_to_chart": stats_module.PERCENTILES_TO_CHART,
        },
        theme=theme,
        static_js="\n".join(static_js),
    )
