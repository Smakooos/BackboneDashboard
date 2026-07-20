from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_pdf(filename="network_report.pdf", stats=None, df=None):
    """
    Generate a styled PDF report from dashboard statistics.
    """

    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        spaceAfter=12,
        textColor=colors.HexColor("#1f4e79"),
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
    )

    story = []
    story.append(Paragraph("Djezzy Backbone Dashboard", title_style))
    story.append(Paragraph("Generated report", body_style))
    story.append(Spacer(1, 12))

    if stats:
        story.append(Paragraph("Summary", styles["Heading2"]))
        if isinstance(stats, dict):
            for key, value in stats.items():
                if isinstance(value, dict):
                    for nested_key, nested_value in value.items():
                        story.append(Paragraph(f"• {nested_key}: {nested_value}", body_style))
                else:
                    story.append(Paragraph(f"• {key}: {value}", body_style))
        else:
            story.append(Paragraph(str(stats), body_style))
        story.append(Spacer(1, 12))

    if df is not None and not df.empty:
        story.append(Paragraph("Data Preview", styles["Heading2"]))
        preview = df.head(5).copy()
        columns = list(preview.columns[:5])
        rows = [[col for col in columns]]
        for _, row in preview.iterrows():
            rows.append([row[col] for col in columns])

        table = Table(rows, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(table)

    doc.build(story)
    print(f"PDF generated successfully: {output_path}")