"""
Ultra-Clean Executive Prediction PDF & Image Generator
Generates a clean, sleek, clutter-free executive prediction report.
Removes all technical jargon, Z3 solver footnotes, proof certificates, and data source labels.
"""

import sys
import os
import json
import time

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont


def register_japanese_fonts():
    try:
        registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
        registerFont(UnicodeCIDFont('HeiseiMin-W3'))
        return 'HeiseiKakuGo-W5'
    except Exception:
        pass

    try:
        font_path = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
        if os.path.exists(font_path):
            registerFont(TTFont('JapaneseFont', font_path))
            return 'JapaneseFont'
    except Exception:
        pass

    return 'Helvetica'


def generate_executive_prediction_pdf(
    json_path: str = "reports/tomorrow_dual_signals_20260805.json",
    pdf_out_path: str = "reports/tomorrow_prediction_report_20260805.pdf"
):
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    jp_font = register_japanese_fonts()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    date_target = data.get("prediction_date", "2026-08-05")
    mainstream_list = data.get("mainstream_top10", [])
    hidden_gems_list = data.get("hidden_gems_top10", [])

    doc = SimpleDocTemplate(
        pdf_out_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName=jp_font,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        alignment=0
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName=jp_font,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        alignment=0
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName=jp_font,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0284C7'),
        spaceBefore=10,
        spaceAfter=6
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName=jp_font,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0F172A')
    )

    cell_normal = ParagraphStyle(
        'CellNormal',
        parent=styles['Normal'],
        fontName=jp_font,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    cell_green = ParagraphStyle(
        'CellGreen',
        parent=styles['Normal'],
        fontName=jp_font,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#15803D')
    )

    cell_red = ParagraphStyle(
        'CellRed',
        parent=styles['Normal'],
        fontName=jp_font,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#B91C1C')
    )

    story = []

    # Clean Header
    story.append(Paragraph("日本株AI予測・買付推奨レポート", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>対象日:</b> {date_target} 市場オープン (08:30 寄前トリガー)", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=12))

    def build_table(universe_signals, title_name):
        story.append(Paragraph(title_name, h2_style))
        story.append(Spacer(1, 4))

        headers = [
            Paragraph("順位", cell_bold),
            Paragraph("コード", cell_bold),
            Paragraph("銘柄名・企業名", cell_bold),
            Paragraph("買付目安", cell_bold),
            Paragraph("利確目標 (TP)", cell_bold),
            Paragraph("損切境界 (SL)", cell_bold),
            Paragraph("RR比", cell_bold)
        ]

        table_data = [headers]

        for idx, item in enumerate(universe_signals, start=1):
            t_code = item["ticker"]
            name = item["company_name"]
            entry = f"¥{item['entry_price']:,.1f}"
            tp = f"¥{item['take_profit']:,.1f} (+{item['tp_pct']}%)"
            sl = f"¥{item['stop_loss']:,.1f} ({item['sl_pct']}%)"
            rr = f"{item['risk_reward']:.2f}"

            row = [
                Paragraph(str(idx), cell_bold),
                Paragraph(t_code, cell_bold),
                Paragraph(name, cell_normal),
                Paragraph(entry, cell_normal),
                Paragraph(tp, cell_green),
                Paragraph(sl, cell_red),
                Paragraph(rr, cell_bold)
            ]
            table_data.append(row)

        t = Table(table_data, colWidths=[30, 55, 145, 75, 110, 100, 65])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#CBD5E1')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        return t

    # 1. 王道部門 (Mainstream)
    t1 = build_table(mainstream_list, "1. 王道部門 TOP 10 (東証大型・主力株)")
    story.append(t1)
    story.append(Spacer(1, 14))

    # 2. 隠れ銘柄部門 (Hidden Gems)
    t2 = build_table(hidden_gems_list, "2. 隠れ銘柄部門 TOP 10 (高成長中小型株)")
    story.append(t2)

    doc.build(story)
    print(f"✔ Ultra-Clean Executive Report created: {pdf_out_path}")


if __name__ == "__main__":
    generate_executive_prediction_pdf()
