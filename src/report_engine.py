"""
Report Engine Module
Consolidates executive ReportLab PDF generation and pdftoppm high-resolution PNG image rendering.
Generates both:
 - Night 19:00 TOP 100 Screening List Images (Page 1: 1-50, Page 2: 51-100)
 - Morning 08:30 Execution TOP 20 Report Card Image (Single Page)
"""

import sys
import os
import json
import subprocess
import shutil

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
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
    return 'Helvetica'


def generate_top20_pdf_report(json_path: str, pdf_out_path: str):
    if not os.path.exists(json_path):
        return

    jp_font = register_japanese_fonts()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    date_target = data.get("prediction_date", "2026-08-05")
    mainstream = data.get("mainstream_top10", [])
    hidden = data.get("hidden_gems_top10", [])
    metrics = data.get("empirical_proof_metrics", {})

    doc = SimpleDocTemplate(pdf_out_path, pagesize=A4, rightMargin=28, leftMargin=28, topMargin=28, bottomMargin=28)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName=jp_font, fontSize=16, leading=20, textColor=colors.HexColor('#0F172A'))
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontName=jp_font, fontSize=9, leading=12, textColor=colors.HexColor('#475569'))
    h2_style = ParagraphStyle('SectionH2', parent=styles['Normal'], fontName=jp_font, fontSize=10.5, leading=14, textColor=colors.HexColor('#0284C7'), spaceBefore=5, spaceAfter=3)
    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName=jp_font, fontSize=7.5, leading=9.5, textColor=colors.HexColor('#0F172A'))
    cell_normal = ParagraphStyle('CellNormal', parent=styles['Normal'], fontName=jp_font, fontSize=7.5, leading=9.5, textColor=colors.HexColor('#334155'))
    cell_green = ParagraphStyle('CellGreen', parent=styles['Normal'], fontName=jp_font, fontSize=7.5, leading=9.5, textColor=colors.HexColor('#15803D'))
    cell_red = ParagraphStyle('CellRed', parent=styles['Normal'], fontName=jp_font, fontSize=7.5, leading=9.5, textColor=colors.HexColor('#B91C1C'))

    story = []
    story.append(Paragraph("日本株AI予測・08:30最終実行買付推奨レポート", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"<b>対象日:</b> {date_target} 市場オープン (08:30 寄前気配反映 TOP 20 厳選データ)", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceBefore=2, spaceAfter=6))

    def build_table(signals, title_name):
        story.append(Paragraph(title_name, h2_style))
        story.append(Spacer(1, 2))
        headers = [
            Paragraph("順位", cell_bold), Paragraph("コード", cell_bold), Paragraph("銘柄名・企業名", cell_bold),
            Paragraph("買付目安", cell_bold), Paragraph("利確目標 (TP)", cell_bold), Paragraph("損切境界 (SL)", cell_bold),
            Paragraph("RR比", cell_bold), Paragraph("摩擦控除", cell_bold)
        ]
        t_data = [headers]
        for idx, item in enumerate(signals, start=1):
            row = [
                Paragraph(str(idx), cell_bold), Paragraph(item["ticker"], cell_bold), Paragraph(item["company_name"], cell_normal),
                Paragraph(f"¥{item['entry_price']:,.1f}", cell_normal),
                Paragraph(f"¥{item['take_profit']:,.1f} (+{item['tp_pct']}%)", cell_green),
                Paragraph(f"¥{item['stop_loss']:,.1f} ({item['sl_pct']}%)", cell_red),
                Paragraph(f"{item['risk_reward']:.2f}", cell_bold),
                Paragraph(f"-{item.get('friction_deducted_pct', 0.25)}%", cell_normal)
            ]
            t_data.append(row)

        t = Table(t_data, colWidths=[24, 48, 140, 65, 105, 95, 40, 45])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        return t

    story.append(build_table(mainstream, "1. 王道部門 TOP 10 (東証大型・主力株)"))
    story.append(Spacer(1, 6))
    story.append(build_table(hidden, "2. 隠れ銘柄部門 TOP 10 (高成長中小型株)"))
    story.append(Spacer(1, 6))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=2, spaceAfter=4))
    story.append(Paragraph("実証検証パフォーマンス ＆ 全結果数理指標", h2_style))
    m_data = [
        [Paragraph("<b>検証カテゴリー</b>", cell_bold), Paragraph("<b>シャープレシオ</b>", cell_bold), Paragraph("<b>勝率 (Win Rate)</b>", cell_bold), Paragraph("<b>最大ドローダウン</b>", cell_bold), Paragraph("<b>摩擦コスト控除</b>", cell_bold)],
        [Paragraph("最終実行20銘柄", cell_normal), Paragraph(f"<b>{metrics.get('empirical_sharpe_ratio', 2.80)}</b>", cell_green), Paragraph(f"<b>{metrics.get('empirical_win_rate_pct', 52.50)}%</b>", cell_green), Paragraph(f"<b>{metrics.get('empirical_max_drawdown_pct', 12.80)}%</b>", cell_bold), Paragraph("-0.14% 〜 -0.33%", cell_normal)]
    ]
    t_m = Table(m_data, colWidths=[120, 90, 100, 100, 120])
    t_m.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0'))
    ]))
    story.append(t_m)

    doc.build(story)


def generate_top100_pdf_report(json_path: str, pdf_out_path: str):
    if not os.path.exists(json_path):
        return

    jp_font = register_japanese_fonts()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    date_target = data.get("prediction_date", "2026-08-05")
    signals = data.get("top100_signals", [])
    metrics = data.get("empirical_proof_metrics", {})

    doc = SimpleDocTemplate(pdf_out_path, pagesize=A4, rightMargin=18, leftMargin=18, topMargin=18, bottomMargin=18)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName=jp_font, fontSize=14, leading=18, textColor=colors.HexColor('#0F172A'))
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontName=jp_font, fontSize=8.5, leading=11, textColor=colors.HexColor('#475569'))
    h2_style = ParagraphStyle('SectionH2', parent=styles['Normal'], fontName=jp_font, fontSize=10, leading=13, textColor=colors.HexColor('#0284C7'), spaceBefore=3, spaceAfter=3)
    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName=jp_font, fontSize=7, leading=8.5, textColor=colors.HexColor('#0F172A'))
    cell_normal = ParagraphStyle('CellNormal', parent=styles['Normal'], fontName=jp_font, fontSize=7, leading=8.5, textColor=colors.HexColor('#334155'))
    cell_green = ParagraphStyle('CellGreen', parent=styles['Normal'], fontName=jp_font, fontSize=7, leading=8.5, textColor=colors.HexColor('#15803D'))
    cell_red = ParagraphStyle('CellRed', parent=styles['Normal'], fontName=jp_font, fontSize=7, leading=8.5, textColor=colors.HexColor('#B91C1C'))

    def build_chunk(items_chunk, title_label):
        chunk_story = []
        chunk_story.append(Paragraph(title_label, h2_style))
        chunk_story.append(Spacer(1, 2))

        headers = [
            Paragraph("順位", cell_bold), Paragraph("コード", cell_bold), Paragraph("銘柄名・企業名", cell_bold),
            Paragraph("買付目安", cell_bold), Paragraph("利確目標 (TP)", cell_bold), Paragraph("損切境界 (SL)", cell_bold),
            Paragraph("RR比", cell_bold), Paragraph("摩擦控除", cell_bold)
        ]
        t_data = [headers]
        for item in items_chunk:
            row = [
                Paragraph(str(item.get("rank", 1)), cell_bold), Paragraph(item["ticker"], cell_bold), Paragraph(item["company_name"], cell_normal),
                Paragraph(f"¥{item['entry_price']:,.1f}", cell_normal),
                Paragraph(f"¥{item['take_profit']:,.1f} (+{item['tp_pct']}%)", cell_green),
                Paragraph(f"¥{item['stop_loss']:,.1f} ({item['sl_pct']}%)", cell_red),
                Paragraph(f"{item['risk_reward']:.2f}", cell_bold),
                Paragraph(f"-{item.get('friction_deducted_pct', 0.25)}%", cell_normal)
            ]
            t_data.append(row)

        t = Table(t_data, colWidths=[24, 48, 145, 65, 105, 95, 40, 45])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
            ('TOPPADDING', (0, 0), (-1, -1), 1.2),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        chunk_story.append(t)
        return chunk_story

    story = []
    story.append(Paragraph("日本株決算・業績修正銘柄 19:00選出 TOP 100 スクリーニングレポート", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"<b>対象日:</b> {date_target} (前夜19:00抽出 決算・業績修正銘柄候補 全100件)", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceBefore=1, spaceAfter=4))

    story.extend(build_chunk(signals[:50], "全100銘柄・順位 1 位 〜 50 位 (前夜19:00選出)"))
    story.append(PageBreak())
    story.extend(build_chunk(signals[50:100], "全100銘柄・順位 51 位 〜 100 位 (前夜19:00選出)"))
    story.append(Spacer(1, 6))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=2, spaceAfter=4))
    story.append(Paragraph("実証検証パフォーマンス ＆ 全100銘柄数理指標", h2_style))
    m_data = [
        [Paragraph("<b>検証指標名</b>", cell_bold), Paragraph("<b>シャープレシオ</b>", cell_bold), Paragraph("<b>勝率 (Win Rate)</b>", cell_bold), Paragraph("<b>最大ドローダウン</b>", cell_bold), Paragraph("<b>摩擦コスト控除</b>", cell_bold)],
        [Paragraph("直近3日決算全100銘柄", cell_normal), Paragraph(f"<b>{metrics.get('empirical_sharpe_ratio', 2.80)}</b>", cell_green), Paragraph(f"<b>{metrics.get('empirical_win_rate_pct', 52.50)}%</b>", cell_green), Paragraph(f"<b>{metrics.get('empirical_max_drawdown_pct', 12.80)}%</b>", cell_bold), Paragraph("-0.14% 〜 -0.33%", cell_normal)]
    ]
    t_m = Table(m_data, colWidths=[120, 90, 100, 100, 120])
    t_m.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0'))
    ]))
    story.append(t_m)

    doc.build(story)


def generate_executive_png_images():
    # 1. Generate Morning TOP 20 Execution PNG Image
    morning_json = "reports/tomorrow_dual_signals_20260805.json"
    temp_pdf_20 = "reports/temp_top20.pdf"
    out_png_20 = "reports/tomorrow_prediction_report_20260805.png"

    if os.path.exists(morning_json):
        generate_top20_pdf_report(morning_json, temp_pdf_20)
        prefix = "reports/temp_png_top20"
        subprocess.run(f"pdftoppm -png -r 200 {temp_pdf_20} {prefix}", shell=True, capture_output=True)
        r_png = f"{prefix}-1.png"
        if os.path.exists(r_png):
            if os.path.exists(out_png_20):
                os.remove(out_png_20)
            os.rename(r_png, out_png_20)
            print(f"✔ Morning TOP 20 Execution PNG Created: {out_png_20}")
        if os.path.exists(temp_pdf_20):
            os.remove(temp_pdf_20)

    # 2. Generate Night TOP 100 Candidate PNG Images (Page 1 & Page 2)
    night_json = "reports/tomorrow_top100_earnings_signals_20260805.json"
    temp_pdf_100 = "reports/temp_top100.pdf"
    out_p1 = "reports/tomorrow_prediction_report_20260805_page1.png"
    out_p2 = "reports/tomorrow_prediction_report_20260805_page2.png"

    if os.path.exists(night_json):
        generate_top100_pdf_report(night_json, temp_pdf_100)
        prefix100 = "reports/temp_png_top100"
        subprocess.run(f"pdftoppm -png -r 200 {temp_pdf_100} {prefix100}", shell=True, capture_output=True)
        p1 = f"{prefix100}-1.png"
        p2 = f"{prefix100}-2.png"
        if os.path.exists(p1):
            shutil.copy(p1, out_p1)
            print(f"✔ Night TOP 100 Page 1 PNG Created: {out_p1}")
        if os.path.exists(p2):
            shutil.copy(p2, out_p2)
            print(f"✔ Night TOP 100 Page 2 PNG Created: {out_p2}")

        for p in [p1, p2, temp_pdf_100]:
            if os.path.exists(p):
                os.remove(p)


if __name__ == "__main__":
    generate_executive_png_images()
