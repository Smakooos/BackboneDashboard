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


from flask import send_file

from reports.pdf_generator import generate_pdf


@app.route("/download-report")
def download_report():

    df = load_csv("data/sample.csv")

    stats = compute_statistics(df)

    filename = "generated_reports/network_report.pdf"

    generate_pdf(
        filename,
        stats,
        df
    )

    return send_file(
        filename,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)