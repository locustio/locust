from jinja2 import Environment, FileSystemLoader
import os
import glob
import pathlib
import datetime
from itertools import chain
from .stats import sort_stats
from . import stats as stats_module
from .user.inspectuser import get_ratio
from html import escape
from json import dumps
from .runners import MasterRunner, STATE_STOPPED, STATE_STOPPING


PERCENTILES_FOR_HTML_REPORT = [0.50, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]


def render_template(file, template_path, **kwargs):
    env = Environment(loader=FileSystemLoader(template_path), extensions=["jinja2.ext.do"])
    template = env.get_template(file)
    return template.render(**kwargs)


def get_html_report(
    environment,
    show_download_link=True,
    use_modern_ui=False,
    theme="",
):
    root_path = os.path.dirname(os.path.abspath(__file__))
    if use_modern_ui:
        static_path = os.path.join(root_path, "webui", "dist", "assets")
        template_path = os.path.join(root_path, "webui", "dist")
    else:
        static_path = os.path.join(root_path, "static")
        template_path = os.path.join(root_path, "templates")

    stats = environment.runner.stats

    start_ts = stats.start_time
    start_time = datetime.datetime.utcfromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S")

    end_ts = stats.last_request_timestamp
    if end_ts:
        end_time = datetime.datetime.utcfromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S")
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

    history = stats.history

    static_js = []
    if use_modern_ui:
        js_files = [os.path.basename(filepath) for filepath in glob.glob(os.path.join(static_path, "*.js"))]
    else:
        js_files = ["jquery-1.11.3.min.js", "echarts.common.min.js", "vintage.js", "chart.js", "tasks.js"]

    for js_file in js_files:
        path = os.path.join(static_path, js_file)
        static_js.append("// " + js_file + "\n")
        with open(path, encoding="utf8") as f:
            static_js.append(f.read())
        static_js.extend(["", ""])

    if not use_modern_ui:
        static_css = []
        css_files = ["tables.css"]
        for css_file in css_files:
            path = os.path.join(static_path, "css", css_file)
            static_css.append("/* " + css_file + " */")
            with open(path, encoding="utf8") as f:
                static_css.append(f.read())
            static_css.extend(["", ""])

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

    if use_modern_ui:
        res = render_template(
            "report.html",
            template_path,
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
                "percentiles_to_chart": stats_module.MODERN_UI_PERCENTILES_TO_CHART,
            },
            theme=theme,
            static_js="\n".join(static_js),
        )
    else:
        res = render_template(
            "report.html",
            template_path,
            int=int,
            round=round,
            escape=escape,
            str=str,
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
            locustfile=environment.locustfile,
            tasks=dumps(task_data),
            percentile1=stats_module.PERCENTILES_TO_CHART[0],
            percentile2=stats_module.PERCENTILES_TO_CHART[1],
        )

    return res
