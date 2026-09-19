import os
from datetime import datetime
from io import BytesIO
from pathlib import Path

from flask import Flask, render_template, send_file

from utils.parser import load_csv
from utils.analyser import compute_statistics, empty_statistics
from reports.pdf_generator import generate_pdf

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "network_metrics.csv"


def get_stats():
    return compute_statistics(load_csv(DATA_FILE)) or empty_statistics()


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


@app.route("/download-report")
def download_report():
    df = load_csv(DATA_FILE)
    stats = compute_statistics(df) or empty_statistics()
    report = BytesIO()
    generate_pdf(report, stats, df)
    report.seek(0)
    return send_file(
        report,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"network-report-{datetime.now():%Y%m%d-%H%M%S}.pdf",
    )


if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
    )
