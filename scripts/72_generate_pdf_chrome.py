import subprocess
import os

REPORTS_DIR = r"C:\Users\Engin Dalga\Documents\GitHub\halusinasyon\hls_new\k2_nli\reports"
INPUT_HTML = os.path.join(REPORTS_DIR, "COMPREHENSIVE_OOD_EVALUATION_REPORT.html")
OUTPUT_PDF = os.path.join(REPORTS_DIR, "COMPREHENSIVE_OOD_EVALUATION_REPORT.pdf")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def convert_with_chrome():
    if not os.path.exists(CHROME_PATH):
        print(f"Chrome not found at {CHROME_PATH}")
        return False
        
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={OUTPUT_PDF}",
        f"file:///{INPUT_HTML.replace(chr(92), '/')}"
    ]
    
    print("Running command:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPORTS_DIR)
    
    if result.returncode == 0:
        print(f"PDF successfully generated at: {OUTPUT_PDF}")
        return True
    else:
        print("Error generating PDF:")
        print(result.stderr)
        return False

if __name__ == "__main__":
    convert_with_chrome()
