"""
Executive High-Res PNG Image Report Generator for TOP 100 Earnings Predictions
Renders Page 1 (Rank 1-50) and Page 2 (Rank 51-100) into crisp PNG images for LINE attachment.
"""

import sys
import os
import subprocess
import shutil
from pdf_report_generator import generate_top100_pdf_report


def generate_executive_prediction_image(
    png_out_path: str = "reports/tomorrow_prediction_report_20260805.png"
):
    print("======================================================================")
    print(" 🖼️ GENERATING FULL TOP 100 HIGH-RES PNG REPORT FOR LINE ATTACHMENT")
    print("======================================================================")

    pdf_temp = "reports/tomorrow_top100_prediction_report_temp.pdf"
    generate_top100_pdf_report(pdf_out_path=pdf_temp)

    if not os.path.exists(pdf_temp):
        print("Error: Temporary PDF could not be generated.")
        return

    prefix = "reports/temp_top100_png_render"
    cmd = f"pdftoppm -png -r 200 {pdf_temp} {prefix}"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    page1_png = f"{prefix}-1.png"
    page2_png = f"{prefix}-2.png"

    target_page1 = "reports/tomorrow_prediction_report_20260805_page1.png"
    target_page2 = "reports/tomorrow_prediction_report_20260805_page2.png"

    if os.path.exists(page1_png):
        shutil.copy(page1_png, target_page1)
        shutil.copy(page1_png, png_out_path)
        print(f"✔ FULL TOP 100 High-resolution PNG (Rank 1-50): {target_page1}")

    if os.path.exists(page2_png):
        shutil.copy(page2_png, target_page2)
        print(f"✔ FULL TOP 100 High-resolution PNG (Rank 51-100): {target_page2}")

    # Clean temporary pdftoppm outputs
    for p in [page1_png, page2_png, pdf_temp]:
        if os.path.exists(p):
            os.remove(p)


if __name__ == "__main__":
    generate_executive_prediction_image()
