import os
import traceback
from flask import Flask, __version__, jsonify, make_response, url_for, redirect, request
from lib.iex_to_ics import CalendarIEX, CalendarTiger, get_ipo_info_html
from lib.common import read_file, expired_for_seconds
from lib.tiger_api import get_ipo_calendar

app = Flask(__name__)
DEBUG = bool(os.getenv("DEBUG"))


from functools import wraps


def dict_as_json(fn):
    @wraps(fn)
    def _fn(*args, **kwargs):
        return jsonify(**fn(*args, **kwargs))

    return _fn


def wrap_exception(fn):
    @wraps(fn)
    def _fn(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            response = make_response(
                {"exception": {"str": str(e), "type": str(type(e))}}
            )
            response.headers["Content-Type"] = "application/json"
            response.status_code = 500
            return response

    return _fn


def text_as_mime(mime):
    def decorator(fn):
        @wraps(fn)
        def _fn(*args, **kwargs):
            rv = fn(*args, **kwargs)
            response = make_response(rv)
            response.headers["Content-Type"] = mime
            return response

        return _fn

    return decorator


@app.route("/")
def index():
    return redirect("/site-map")


@app.route("/site-map")
@dict_as_json
def site_map():
    links = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != "static":
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links[rule.endpoint] = {"url": url, "methods": list(rule.methods)}
    return {"urls": links}


@app.route("/status")
@dict_as_json
def status():
    return {
        "flask": {"version": __version__},
        "status": "healthy",
        "files": os.listdir("/tmp"),
    }


@app.route("/api/itiger.com/calendar/api")
@wrap_exception
@dict_as_json
def tiger_calendar():
    return get_ipo_calendar().json()


@app.route("/api/nasdaq.com/symbol/<symbol>", defaults={"symbol": "QQQ"})
@wrap_exception
@text_as_mime("text/html")
def nasdaq_symbol_detail(symbol):
    return get_ipo_info_html(symbol, enable=True)


@app.route("/calendar/ipo-iex.ics")
@wrap_exception
@text_as_mime("text/plain" if DEBUG else "text/calendar")
def ipo_iex():
    cld = CalendarIEX()
    output = cld.get_output_path()
    text = read_file(output)
    if expired_for_seconds(cld.name, 60 * 60 * 24) or text is None:
        cld.gen_ics()
    return read_file(output) or "FILE NOT FOUND"


# Tiger IPO calendar


@app.route("/calendar/ipo-tiger.ics")
@wrap_exception
@text_as_mime("text/plain" if DEBUG else "text/calendar")
def ipo_tiger():
    cld = CalendarTiger()
    output = cld.get_output_path()
    text = read_file(output)
    if expired_for_seconds(cld.name, 60 * 60 * 3) or text is None:
        cld.gen_ics()
    return read_file(output) or "FILE NOT FOUND"


@app.route("/calendar/ipo-tiger-us.ics")
@wrap_exception
@text_as_mime("text/plain" if DEBUG else "text/calendar")
def ipo_tiger_us():
    cld = CalendarTiger(filter_fn=lambda x: x["market"] == "US")
    cld.name = "ipo-tiger-us"
    cld.cal_name = "IPO (tiger) (US)"

    output = cld.get_output_path()
    text = read_file(output)
    if expired_for_seconds(cld.name, 60 * 60 * 3) or text is None:
        cld.gen_ics()
    return read_file(output) or "FILE NOT FOUND"


@app.route("/calendar/ipo-tiger-hk.ics")
@wrap_exception
@text_as_mime("text/plain" if DEBUG else "text/calendar")
def ipo_tiger_hk():
    cld = CalendarTiger(filter_fn=lambda x: x["market"] == "HK")
    cld.name = "ipo-tiger-hk"
    cld.cal_name = "IPO (tiger) (HK)"

    output = cld.get_output_path()
    text = read_file(output)
    if expired_for_seconds(cld.name, 60 * 60 * 3) or text is None:
        cld.gen_ics()
    return read_file(output) or "FILE NOT FOUND"


@app.route("/calendar/ipo-tiger-mainland.ics")
@wrap_exception
@text_as_mime("text/plain" if DEBUG else "text/calendar")
def ipo_tiger_mainland():
    cld = CalendarTiger(filter_fn=lambda x: x["market"] in ["SZ", "SH"])
    cld.name = "ipo-tiger-mainland"
    cld.cal_name = "IPO (tiger) (SH/SZ)"

    output = cld.get_output_path()
    text = read_file(output)
    if expired_for_seconds(cld.name, 60 * 60 * 3) or text is None:
        cld.gen_ics()
    return read_file(output) or "FILE NOT FOUND"


# Tiger IPO Calendar RSS


def route_for_rss(path_prefix):
    def decorator(fn):
        origin_name = fn.__name__
        for t in ["atom", "rss"]:
            # rename for app.route
            fn.__name__ += f"_{t}"
            mime = {"atom": "application/rss+xml", "rss": "application/rss+xml"}[t]
            mine_fn = text_as_mime(mime)(fn)
            app.route(f"{path_prefix}.{t}")(mine_fn)

        # rename back
        fn.__name__ = origin_name
        return fn

    return decorator


def get_rss():
    url = request.url
    rss = None
    if url.endswith(".atom"):
        rss = "atom"
    elif url.endswith(".rss"):
        rss = "rss"
    return rss


@route_for_rss("/calendar/ipo-tiger")
@wrap_exception
def ipo_tiger_rss():
    rss = get_rss()
    cld = CalendarTiger()
    cld.name += rss
    output = cld.get_output_path(rss)
    text = read_file(output)

    if expired_for_seconds(cld.name, 60 * 60 * 3) or text is None:
        cld.gen_ics(rss)
    return read_file(output) or "FILE NOT FOUND"


@route_for_rss("/calendar/ipo-tiger-us")
@wrap_exception
def ipo_tiger_rss_us():
    rss = get_rss()
    cld = CalendarTiger(filter_fn=lambda x: x["market"] == "US")
    cld.name = "ipo-tiger-us" + "-" + rss
    cld.cal_name = "IPO (tiger) (US)"

    output = cld.get_output_path(rss)
    text = read_file(output)
    if expired_for_seconds(cld.name, 60 * 60 * 3) or text is None:
        cld.gen_ics(rss)
    return read_file(output) or "FILE NOT FOUND"


@route_for_rss("/calendar/ipo-tiger-hk")
@wrap_exception
def ipo_tiger_rss_hk():
    rss = get_rss()
    cld = CalendarTiger(filter_fn=lambda x: x["market"] == "HK")
    cld.name = "ipo-tiger-hk" + "-" + rss
    cld.cal_name = "IPO (tiger) (HK)"

    output = cld.get_output_path(rss)
    text = read_file(output)
    if expired_for_seconds(cld.name, 60 * 60 * 3) or text is None:
        cld.gen_ics(rss)
    return read_file(output) or "FILE NOT FOUND"


@route_for_rss("/calendar/ipo-tiger-mainland")
@wrap_exception
def ipo_tiger_rss_mainland():
    rss = get_rss()
    cld = CalendarTiger(filter_fn=lambda x: x["market"] in ["SZ", "SH"])
    cld.name = "ipo-tiger-mainland" + "-" + rss
    cld.cal_name = "IPO (tiger) (SH/SZ)"

    output = cld.get_output_path(rss)
    text = read_file(output)
    if expired_for_seconds(cld.name, 60 * 60 * 3) or text is None:
        cld.gen_ics(rss)
    return read_file(output) or "FILE NOT FOUND"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=DEBUG)
