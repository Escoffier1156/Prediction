"""
Executive Image (PNG) Prediction Report Generator
Automatically generates high-resolution executive PNG report images (for LINE/Discord image attachment)
directly from prediction JSON data via ReportLab and pdftoppm.
"""

import sys
import os
import json
import time
import subprocess

from pdf_report_generator import generate_executive_prediction_pdf


def generate_executive_prediction_image(
    json_path: str = "reports/tomorrow_dual_signals_20260805.json",
    png_out_path: str = "reports/tomorrow_prediction_report_20260805.png"
):
    print("======================================================================")
    print(" 🖼️ GENERATING EXECUTIVE HIGH-RES PNG REPORT FOR LINE ATTACHMENT")
    print("======================================================================")

    pdf_temp = "reports/tomorrow_prediction_report_temp.pdf"
    generate_executive_prediction_pdf(json_path=json_path, pdf_out_path=pdf_temp)

    if not os.path.exists(pdf_temp):
        print("Error: Temporary PDF could not be generated.")
        return

    # Convert PDF to high-res PNG via pdftoppm (200 DPI for crisp mobile display)
    prefix = "reports/temp_png_render"
    cmd = f"pdftoppm -png -r 200 {pdf_temp} {prefix}"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    rendered_png = f"{prefix}-1.png"
    if os.path.exists(rendered_png):
        if os.path.exists(png_out_path):
            os.remove(png_out_path)
        os.rename(rendered_png, png_out_path)
        print(f"✔ High-resolution PNG Report created: {png_out_path}")
    else:
        print("Warning: PNG conversion fallback required.")

    if os.path.exists(pdf_temp):
        os.remove(pdf_temp)


if __name__ == "__main__":
    generate_executive_prediction_image()
