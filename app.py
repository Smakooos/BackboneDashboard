from flask import Flask, render_template

from utils.parser import load_csv
from utils.analyser import compute_statistics

app = Flask(__name__)


def get_stats():
    df = load_csv("data/sample.csv")
    return compute_statistics(df)


@app.route("/")
@app.route("/dashboard")
def dashboard():

    stats = get_stats()

    return render_template(
        "dashboard.html",
        stats=stats,
        active_page="dashboard"
    )


@app.route("/analytics")
def analytics():

    stats = get_stats()

    return render_template(
        "analytics.html",
        stats=stats,
        active_page="analytics"
    )


@app.route("/reports")
def reports():

    return render_template(
        "reports.html",
        active_page="reports"
    )


@app.route("/project")
def project():

    return render_template(
        "project.html",
        active_page="project"
    )


@app.route("/faq")
def faq():

    return render_template(
        "faq.html",
        active_page="faq"
    )


if __name__ == "__main__":
    app.run(debug=True)