from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _to_python_type(value):
    """Convert numpy/pandas types to native Python types for ReportLab compatibility."""
    if hasattr(value, 'item'):  # numpy scalar
        return value.item()
    if hasattr(value, '__int__'):
        if isinstance(value, (bool, int)):
            return value
    if isinstance(value, (int, float, str, bool, type(None))):
        return value
    return str(value)


def _table(rows, widths=None):
    # Convert all values to native Python types
    converted_rows = [
        [_to_python_type(cell) for cell in row]
        for row in rows
    ]
    table = Table(converted_rows, colWidths=widths, repeatRows=1)
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
    
    # Convert stats values to native Python types
    total_devices = _to_python_type(stats["total_devices"])
    total_interfaces = _to_python_type(stats["total_interfaces"])
    avg_in_mbps = _to_python_type(stats["avg_in_mbps"])
    avg_out_mbps = _to_python_type(stats["avg_out_mbps"])
    
    story = [
        Paragraph("Djezzy Backbone Dashboard", title),
        Paragraph("Network health report — latest SNMP snapshot", styles["BodyText"]),
        Spacer(1, 14), Paragraph("Summary", styles["Heading2"]),
        _table([
            ["Metric", "Value"], 
            ["Monitored devices", total_devices],
            ["Monitored interfaces", total_interfaces],
            ["Average inbound throughput", f'{avg_in_mbps} Mbps'],
            ["Average outbound throughput", f'{avg_out_mbps} Mbps'],
        ], widths=[260, 220]),
        Spacer(1, 14), Paragraph("Interface status", styles["Heading2"]),
        _table([
            ["Status", "Interfaces"], 
            ["UP", _to_python_type(stats["status"]["UP"])],
            ["DOWN", _to_python_type(stats["status"]["DOWN"])],
            ["WARNING", _to_python_type(stats["status"]["WARNING"])],
            ["CRITICAL", _to_python_type(stats["status"]["CRITICAL"])],
        ], widths=[260, 220]),
        Spacer(1, 14), Paragraph("Device throughput and status", styles["Heading2"]),
        _table(
            [["Device", "IP", "Inbound (Mbps)", "Outbound (Mbps)", "Worst status"]] + [
                [
                    escape(str(_to_python_type(item["device"]))),
                    escape(str(_to_python_type(item["ip"]))),
                    _to_python_type(item["in_mbps"]),
                    _to_python_type(item["out_mbps"]),
                    escape(str(_to_python_type(item["status"])))
                ]
                for item in stats["device_breakdown"]
            ], 
            widths=[100, 120, 120, 120, 80]
        ),
    ]
    if df is not None and not df.empty:
        story.extend([Spacer(1, 14), Paragraph("Latest data preview", styles["Heading2"]),
            _table([[escape(str(column)) for column in df.columns]] + [
                [escape(str(_to_python_type(value))) for value in row]
                for row in df.tail(10).itertuples(index=False, name=None)
            ])])
    doc.build(story)
