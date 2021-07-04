from jinja2 import Environment, FileSystemLoader
import os
import pathlib
import datetime
from itertools import chain
from .stats import sort_stats


def render_template(file, **kwargs):
    templates_path = os.path.join(pathlib.Path(__file__).parent.absolute(), "templates")
    env = Environment(loader=FileSystemLoader(templates_path), extensions=["jinja2.ext.do"])
    template = env.get_template(file)
    return template.render(**kwargs)


def get_html_report(environment, show_download_link=True):
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
    exceptions_statistics = [
        {**exc, "nodes": ", ".join(exc["nodes"])} for exc in environment.runner.exceptions.values()
    ]

    history = stats.history

    static_js = []
    js_files = ["jquery-1.11.3.min.js", "echarts.common.min.js", "vintage.js", "chart.js"]
    for js_file in js_files:
        path = os.path.join(os.path.dirname(__file__), "static", js_file)
        static_js.append("// " + js_file)
        with open(path, encoding="utf8") as f:
            static_js.append(f.read())
        static_js.extend(["", ""])

    static_css = []
    css_files = ["tables.css"]
    for css_file in css_files:
        path = os.path.join(os.path.dirname(__file__), "static", "css", css_file)
        static_css.append("/* " + css_file + " */")
        with open(path, encoding="utf8") as f:
            static_css.append(f.read())
        static_css.extend(["", ""])

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
        static_js="\n".join(static_js),
        static_css="\n".join(static_css),
        show_download_link=show_download_link,
    )

    return res
