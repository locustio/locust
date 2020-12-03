from jinja2 import Environment, FileSystemLoader
import os
import pathlib
import datetime
from itertools import chain
from .stats import sort_stats


def render_template(file, **kwargs):
    templates_path = os.path.join(pathlib.Path(__file__).parent.absolute(), "templates")
    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template(file)
    return template.render(**kwargs)


def get_html_report(environment):
    stats = environment.runner.stats

    start_ts = stats.start_time
    start_time = datetime.datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S")

    end_ts = stats.last_request_timestamp
    if end_ts:
        end_time = datetime.datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S")
    else:
        end_time = start_time

    host = None
    if environment.host:
        host = environment.host
    elif environment.runner.user_classes:
        all_hosts = set([l.host for l in environment.runner.user_classes])
        if len(all_hosts) == 1:
            host = list(all_hosts)[0]

    requests_statistics = list(chain(sort_stats(stats.entries), [stats.total]))
    failures_statistics = sort_stats(stats.errors)
    exceptions_statistics = []
    for exc in environment.runner.exceptions.values():
        exc["nodes"] = ", ".join(exc["nodes"])
        exceptions_statistics.append(exc)

    history = stats.history

    static_js = ""
    js_files = ["jquery-1.11.3.min.js", "echarts.common.min.js", "vintage.js", "chart.js"]
    for js_file in js_files:
        path = os.path.join(os.path.dirname(__file__), "static", js_file)
        with open(path, encoding="utf8") as f:
            content = f.read()
        static_js += "// " + js_file + "\n"
        static_js += content
        static_js += "\n\n\n"

    res = render_template(
        "report.html",
        int=int,
        round=round,
        requests_statistics=requests_statistics,
        failures_statistics=failures_statistics,
        exceptions_statistics=exceptions_statistics,
        start_time=start_time,
        end_time=end_time,
        host=host,
        history=history,
        static_js=static_js,
    )

    return res
