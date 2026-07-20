from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_pdf(filename="network_report.pdf", stats=None, df=None):
    """Generate a polished and dynamic PDF report for the backbone dashboard."""

    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        spaceAfter=8,
        textColor=colors.HexColor("#C1121F"),
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        spaceAfter=8,
        textColor=colors.HexColor("#1f4e79"),
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#222222"),
    )
    highlight_style = ParagraphStyle(
        "HighlightStyle",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#C1121F"),
    )

    story = []
    story.append(Paragraph("DJEZZY BACKBONE DASHBOARD", title_style))
    story.append(Paragraph("Executive Network Report", subtitle_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y at %H:%M')}", body_style))
    story.append(Spacer(1, 10))

    if stats:
        critical_count = stats.get("status", {}).get("CRITICAL", 0)
        warning_count = stats.get("status", {}).get("WARNING", 0)
        high_cpu = stats.get("alerts", {}).get("high_cpu", 0)
        high_memory = stats.get("alerts", {}).get("high_memory", 0)
        high_latency = stats.get("alerts", {}).get("high_latency", 0)

        summary_text = (
            f"This report summarizes the current backbone monitoring state with {stats.get('total_devices', 0)} devices tracked. "
            f"The network shows {critical_count} critical device(s) and {warning_count} warning device(s). "
            f"Immediate attention is recommended for {high_cpu} high CPU alert(s), {high_memory} high memory alert(s), and {high_latency} high latency alert(s)."
        )
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 14))

        story.append(Paragraph("Key Metrics", subtitle_style))
        summary_rows = [
            ["Metric", "Value"],
            ["Total Devices", stats.get("total_devices", 0)],
            ["Average CPU", f"{stats.get('avg_cpu', 0)}%"],
            ["Average Memory", f"{stats.get('avg_memory', 0)}%"],
            ["Average Bandwidth", f"{stats.get('avg_bandwidth', 0)} Mbps"],
            ["Average Latency", f"{stats.get('avg_latency', 0)} ms"],
        ]
        summary_table = Table(summary_rows, colWidths=[6 * cm, 6 * cm])
        summary_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C1121F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("PADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(summary_table)
        story.append(Spacer(1, 14))

        story.append(Paragraph("Status Overview", subtitle_style))
        status_rows = [
            ["Status", "Devices"],
            ["UP", stats.get("status", {}).get("UP", 0)],
            ["WARNING", stats.get("status", {}).get("WARNING", 0)],
            ["CRITICAL", stats.get("status", {}).get("CRITICAL", 0)],
        ]
        status_table = Table(status_rows, colWidths=[6 * cm, 6 * cm])
        status_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("PADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(status_table)
        story.append(Spacer(1, 14))

        story.append(Paragraph("Operational Recommendations", subtitle_style))
        if critical_count > 0:
            story.append(Paragraph("- Prioritize critical devices immediately to prevent service degradation.", body_style))
        if warning_count > 0:
            story.append(Paragraph("- Monitor warning devices closely and review their trends over the next reporting cycle.", body_style))
        if high_latency > 0:
            story.append(Paragraph("- Investigate latency issues that may impact user experience and data transmission.", body_style))
        if high_cpu == 0 and high_memory == 0 and high_latency == 0:
            story.append(Paragraph("- No major alerts detected. The network is operating within expected ranges.", body_style))
        story.append(Spacer(1, 14))

    if df is not None and not df.empty:
        story.append(Paragraph("Device Inventory", subtitle_style))
        preview = df.head(10).copy()
        inventory_rows = [["Device", "CPU", "Memory", "Bandwidth", "Latency", "Status"]]
        for _, row in preview.iterrows():
            inventory_rows.append([
                row["Device"],
                f"{row['CPU']}%",
                f"{row['Memory']}%",
                f"{row['Bandwidth']} Mbps",
                f"{row['Latency']} ms",
                row["Status"],
            ])

        inventory_table = Table(inventory_rows, repeatRows=1)
        inventory_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C1121F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("PADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(inventory_table)
        story.append(Spacer(1, 16))

    story.append(Paragraph("Prepared by Bouzid Noureddine - ESI", highlight_style))
    story.append(Paragraph("Djezzy Internship Project", body_style))

    doc.build(story)
    print(f"PDF generated successfully: {output_path}")