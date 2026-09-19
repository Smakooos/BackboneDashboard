from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _table(rows, widths=None):
    table = Table(rows, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c4ce")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def generate_pdf(destination, stats, df=None):
    """Build an SNMP network report to a writable stream or filesystem path."""
    if isinstance(destination, (str, Path)):
        output_path = Path(destination)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        destination = str(output_path)

    doc = SimpleDocTemplate(destination, pagesize=letter, rightMargin=36,
                            leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                           fontSize=18, leading=22, textColor=colors.HexColor("#1f4e79"))
    story = [
        Paragraph("Djezzy Backbone Dashboard", title),
        Paragraph("Network health report — latest SNMP snapshot", styles["BodyText"]),
        Spacer(1, 14), Paragraph("Summary", styles["Heading2"]),
        _table([
            ["Metric", "Value"], ["Monitored devices", stats["total_devices"]],
            ["Monitored interfaces", stats["total_interfaces"]],
            ["Average inbound throughput", f'{stats["avg_in_mbps"]} Mbps'],
            ["Average outbound throughput", f'{stats["avg_out_mbps"]} Mbps'],
        ], widths=[260, 220]),
        Spacer(1, 14), Paragraph("Interface status", styles["Heading2"]),
        _table([
            ["Status", "Interfaces"], ["UP", stats["status"]["UP"]],
            ["WARNING", stats["status"]["WARNING"]], ["CRITICAL", stats["status"]["CRITICAL"]],
        ], widths=[260, 220]),
        Spacer(1, 14), Paragraph("Device throughput", styles["Heading2"]),
        _table([["Device", "Inbound (Mbps)", "Outbound (Mbps)", "Worst status"]] + [
            [escape(str(item["device"])), item["in_mbps"], item["out_mbps"], item["status"]]
            for item in stats["device_breakdown"]
        ], widths=[140, 120, 120, 100]),
    ]
    if df is not None and not df.empty:
        story.extend([Spacer(1, 14), Paragraph("Latest data preview", styles["Heading2"]),
            _table([[escape(str(column)) for column in df.columns]] + [
                [escape(str(value)) for value in row]
                for row in df.tail(10).itertuples(index=False, name=None)
            ])])
    doc.build(story)
