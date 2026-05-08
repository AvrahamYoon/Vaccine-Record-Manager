import io
import os

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle


def _register_cjk_font():
    candidates = [
        ("NotoSansCJK", r"C:\Windows\Fonts\NotoSansCJK-Regular.ttc"),
        ("MicrosoftYaHei", r"C:\Windows\Fonts\msyh.ttc"),
        ("MicrosoftYaHei", r"C:\Windows\Fonts\msyh.ttf"),
        ("SimSun", r"C:\Windows\Fonts\simsun.ttc"),
        ("PingFang", "/System/Library/Fonts/PingFang.ttc"),
        ("NotoSansCJK", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    ]
    for name, path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                return name
            except Exception:
                continue
    return "Helvetica"


def build_pdf(
    df: pd.DataFrame,
    title: str,
    generated_label: str,
    total_label: str,
    *,
    col_headers: list[str],
) -> bytes:
    font_name = _register_cjk_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=18 * mm,
        bottomMargin=15 * mm,
    )

    getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title", fontName=font_name, fontSize=16, leading=22, textColor=colors.HexColor("#111827"), spaceAfter=4
    )
    sub_style = ParagraphStyle(
        "sub", fontName=font_name, fontSize=9, leading=13, textColor=colors.HexColor("#6b7280"), spaceAfter=12
    )
    cell_style = ParagraphStyle("cell", fontName=font_name, fontSize=8, leading=11, textColor=colors.HexColor("#1f2937"))
    header_style = ParagraphStyle(
        "header", fontName=font_name, fontSize=8, leading=11, textColor=colors.white, fontWeight="bold"
    )

    col_widths = [10 * mm, 28 * mm, 12 * mm, 22 * mm, 28 * mm, 22 * mm, 10 * mm, 42 * mm]
    header_row = [Paragraph(h, header_style) for h in col_headers]
    data_rows = []
    for _, row in df.iterrows():
        data_rows.append(
            [
                Paragraph(str(int(row["id"])) if pd.notna(row["id"]) else "", cell_style),
                Paragraph(str(row["name"]) if pd.notna(row["name"]) else "", cell_style),
                Paragraph(str(int(row["dose"])) if pd.notna(row["dose"]) else "", cell_style),
                Paragraph(str(row["date"]) if pd.notna(row["date"]) else "", cell_style),
                Paragraph(str(row["manufacturer"]) if pd.notna(row["manufacturer"]) else "", cell_style),
                Paragraph(str(row["batch"]) if pd.notna(row["batch"]) else "", cell_style),
                Paragraph(str(row["arm"]) if pd.notna(row["arm"]) else "", cell_style),
                Paragraph(str(row["provider"]) if pd.notna(row["provider"]) else "", cell_style),
            ]
        )

    table = Table([header_row] + data_rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f7df3")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fb")]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
                ("LINEBELOW", (0, 0), (-1, 0), 0, colors.transparent),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROUNDEDCORNERS", [4, 4, 4, 4]),
            ]
        )
    )

    from datetime import datetime

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    story = [
        Paragraph(title, title_style),
        Paragraph(f"{generated_label} {now_str}　　{total_label} {len(df)}", sub_style),
        table,
    ]
    doc.build(story)
    return buf.getvalue()
