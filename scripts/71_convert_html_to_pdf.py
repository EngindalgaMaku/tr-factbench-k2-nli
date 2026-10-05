import os
from xhtml2pdf import pisa

REPORTS_DIR = r"C:\Users\Engin Dalga\Documents\GitHub\halusinasyon\hls_new\k2_nli\reports"
INPUT_HTML = os.path.join(REPORTS_DIR, "COMPREHENSIVE_OOD_EVALUATION_REPORT.html")
OUTPUT_PDF = os.path.join(REPORTS_DIR, "COMPREHENSIVE_OOD_EVALUATION_REPORT.pdf")

def convert_html_to_pdf(source_html, output_filename):
    with open(source_html, "r", encoding="utf-8") as f:
        source_html_content = f.read()

    with open(output_filename, "wb") as result_file:
        pisa_status = pisa.CreatePDF(
            source_html_content,
            dest=result_file,
            encoding='utf-8'
        )
        
    if pisa_status.err:
        print(f"Error creating PDF: {pisa_status.err}")
    else:
        print(f"PDF successfully created: {output_filename}")

if __name__ == "__main__":
    convert_html_to_pdf(INPUT_HTML, OUTPUT_PDF)
