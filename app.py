import app_config
import identity.web
import requests
from flask import Flask
from flask import Response
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix


__version__ = "0.7.0"

app = Flask(__name__)
app.config.from_object(app_config)
assert app.config["REDIRECT_PATH"] != "/", "REDIRECT_PATH must not be /"
Session(app)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.jinja_env.globals.update(Auth=identity.web.Auth)
auth = identity.web.Auth(
    session=session,
    authority=app.config["AUTHORITY"],
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)


@app.route("/login")
def login() -> Response:
    return render_template(
        "login.html",
        version=__version__,
        **auth.log_in(
            scopes=app_config.SCOPE,
            redirect_uri=url_for("auth_response", _external=True),
            prompt="select_account",
        ),
    )


@app.route(app_config.REDIRECT_PATH)
def auth_response() -> Response:
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    return redirect(url_for("index"))


@app.route("/logout")
def logout() -> Response:
    return redirect(auth.log_out(url_for("index", _external=True)))


@app.route("/")
def index() -> Response:
    if not (app.config["CLIENT_ID"] and app.config["CLIENT_SECRET"]):
        return render_template("config_error.html")
    if not auth.get_user():
        return redirect(url_for("login"))
    return render_template(
        "index.html", user=auth.get_user(), version=__version__
    )


@app.route("/call_downstream_api")
def call_downstream_api() -> Response:
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))

    api_result = requests.get(
        app_config.ENDPOINT,
        headers={"Authorization": "Bearer " + token["access_token"]},
        timeout=30,
    ).json()
    return render_template("display.html", result=api_result)


if __name__ == "__main__":
    app.run()

# Tutorial to configure tenant:
# https://learn.microsoft.com/de-de/entra/identity-platform/\
# quickstart-web-app-python-sign-in?tabs=windows
# Run with: python -m flask run --debug --host=localhost --port=5000
