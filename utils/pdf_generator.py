from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def generate_pdf(filename, stats, df):
    """
    Generate a professional Backbone Network Report.
    """

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        filename,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm
    )

    story = []

    # ======================================================
    # TITLE
    # ======================================================

    story.append(
        Paragraph(
            "<font size='24' color='#C1121F'><b>DJEZZY BACKBONE DASHBOARD</b></font>",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "<font size='18'><b>Network Health Report</b></font>",
            styles["Heading1"]
        )
    )

    story.append(Spacer(1, 15))

    now = datetime.now()

    story.append(
        Paragraph(
            f"<b>Generated on :</b> {now.strftime('%d %B %Y - %H:%M')}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            """
            This report provides an overview of the current health of the
            Djezzy Backbone Network. It includes key performance indicators,
            network status, alerts and an inventory of monitored devices.
            """,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 25))

    # ======================================================
    # GENERAL STATISTICS
    # ======================================================

    story.append(
        Paragraph(
            "<b>GENERAL STATISTICS</b>",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 8))

    summary = [

        ["Metric", "Value"],

        ["Total Devices", stats["total_devices"]],

        ["Average CPU", f'{stats["avg_cpu"]}%'],

        ["Average Memory", f'{stats["avg_memory"]}%'],

        ["Average Bandwidth", f'{stats["avg_bandwidth"]} Mbps'],

        ["Average Latency", f'{stats["avg_latency"]} ms']

    ]

    table = Table(summary, colWidths=[8 * cm, 6 * cm])

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C1121F")),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("FONTSIZE", (0, 0), (-1, -1), 10),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")

    ]))

    story.append(table)

    story.append(Spacer(1, 25))

    # ======================================================
    # NETWORK STATUS
    # ======================================================

    story.append(
        Paragraph(
            "<b>NETWORK STATUS</b>",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 8))

    status_table = [

        ["Status", "Devices"],

        ["UP", stats["status"]["UP"]],

        ["WARNING", stats["status"]["WARNING"]],

        ["CRITICAL", stats["status"]["CRITICAL"]]

    ]

    table = Table(status_table, colWidths=[8 * cm, 6 * cm])

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C1121F")),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

        ("ALIGN", (0, 0), (-1, -1), "CENTER")

    ]))

    story.append(table)

    story.append(Spacer(1, 25))

    # ======================================================
    # ALERTS
    # ======================================================

    story.append(
        Paragraph(
            "<b>ALERT SUMMARY</b>",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 8))

    alerts = [

        ["Alert", "Count"],

        ["High CPU", stats["alerts"]["high_cpu"]],

        ["High Memory", stats["alerts"]["high_memory"]],

        ["High Latency", stats["alerts"]["high_latency"]]

    ]

    table = Table(alerts, colWidths=[8 * cm, 6 * cm])

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C1121F")),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),

        ("ALIGN", (0, 0), (-1, -1), "CENTER")

    ]))

    story.append(table)

    story.append(Spacer(1, 25))

    # ======================================================
    # DEVICE INVENTORY
    # ======================================================

    story.append(
        Paragraph(
            "<b>DEVICE INVENTORY</b>",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 8))

    devices = [["Device", "CPU", "Memory", "Bandwidth", "Latency", "Status"]]

    for _, row in df.iterrows():

        devices.append([

            row["Device"],

            f'{row["CPU"]}%',

            f'{row["Memory"]}%',

            f'{row["Bandwidth"]} Mbps',

            f'{row["Latency"]} ms',

            row["Status"]

        ])

    table = Table(devices)

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C1121F")),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("FONTSIZE", (0, 0), (-1, -1), 9)

    ]))

    story.append(table)

    story.append(Spacer(1, 30))

    # ======================================================
    # FOOTER
    # ======================================================

    story.append(
        Paragraph(
            """
            <font size='9' color='grey'>
            Generated automatically by Djezzy Backbone Dashboard<br/>
            Developed by BOUZID Noureddine - ESI
            </font>
            """,
            styles["BodyText"]
        )
    )

    # Build PDF
    doc.build(story)