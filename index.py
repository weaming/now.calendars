import os
from flask import Flask, __version__, jsonify, make_response, url_for, redirect
from lib.iex_to_ics import get_ics_output, gen_ics
from lib.common import read_file, expired_for_seconds

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


@app.route("/status")
@dict_as_json
def status():
    return {"flask": {"version": __version__}, "status": "healthy"}


@app.route("/calendar/iex-ipo-upcomming.ics")
@wrap_exception
@text_as_mime("text/plain" if DEBUG else "text/calendar")
def ipo_upcomming():
    output = get_ics_output()
    text = read_file(output)
    if expired_for_seconds("iex-ipo-upcomming", 60 * 60 * 24) or text is None:
        gen_ics()
    return read_file(output) or "FILE NOT FOUND"


@app.route("/test")
@text_as_mime("text/plain")
def test_text():
    return "hello"


@app.route("/site-map")
@dict_as_json
def site_map():
    links = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != "static":
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links[rule.endpoint] = {"url": url, "methods": list(rule.methods)}
    return {"urls": links}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=DEBUG)
