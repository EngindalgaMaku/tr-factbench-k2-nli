import os
import json
import markdown
import subprocess

PROJECT_ROOT = r"C:\Users\Engin Dalga\Documents\GitHub\halusinasyon\hls_new\k2_nli"
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "ood_case_study")

DOMAINS = [
    {
        "name": "Tıp (Alzheimer)",
        "data_file": os.path.join(DATA_DIR, "alzheimer_ood_16.jsonl"),
        "results_file": os.path.join(REPORTS_DIR, "experiments", "OOD-ALZHEIMER-CASE-STUDY-v1", "results.jsonl")
    },
    {
        "name": "Hukuk (İş Kanunu)",
        "data_file": os.path.join(DATA_DIR, "legal_ood_16.jsonl"),
        "results_file": os.path.join(REPORTS_DIR, "experiments", "OOD-LEGAL-CASE-STUDY-v1", "results.jsonl")
    },
    {
        "name": "Finans (Eurobond)",
        "data_file": os.path.join(DATA_DIR, "finance_ood_16.jsonl"),
        "results_file": os.path.join(REPORTS_DIR, "experiments", "OOD-FINANCE-CASE-STUDY-v1", "results.jsonl")
    }
]

OUTPUT_MD = os.path.join(REPORTS_DIR, "ACADEMIC_OOD_EVALUATION_REPORT.md")
OUTPUT_HTML = os.path.join(REPORTS_DIR, "ACADEMIC_OOD_EVALUATION_REPORT.html")
OUTPUT_PDF = os.path.join(REPORTS_DIR, "ACADEMIC_OOD_EVALUATION_REPORT.pdf")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def load_jsonl(filepath):
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def generate_markdown():
    md = """# Dağılım Dışı (OOD) Veri Kümelerinde Kademeli Hibrit Mimari Analiz Raporu

**Tarih:** 5 Ekim 2026  
**Yazar:** Engin Dalga  
**Danışman:** Prof. Dr. Serkan Ballı  

## 1. Giriş
Bu raporda, Kademeli Hibrit Mimarinin eğitim verisinde bulunmayan (Dağılım Dışı / Out-of-Distribution) metinlerdeki performansını değerlendirmek amacıyla Tıp (Alzheimer), Hukuk (İş Kanunu) ve Finans (Eurobond) alanlarında oluşturulan toplam 48 vakanın analizi sunulmaktadır. Modellerin verdikleri yanıtlar, hakem mekanizmasının kararları ve sonuçlar vaka bazında listelenmiştir. Her vaka için sorulan soru, referans bağlam ve değerlendirilen iddia açıkça gösterilmiştir.

## 2. Kümülatif Performans Tablosu

| Metrik / Model | Tıp (Alzheimer) | Hukuk (İş Kanunu) | Finans (Eurobond) | Toplam (48 Vaka) |
| :--- | :---: | :---: | :---: | :---: |
| K1 Doğruluğu (ELECTRA-TR) | 15/16 (%93.75) | 14/16 (%87.50) | 15/16 (%93.75) | 44/48 (%91.67) |
| K2 Doğruluğu (Gemma-4+mDeBERTa) | 13/16 (%81.25) | 15/16 (%93.75) | 11/16 (%68.75) | 39/48 (%81.25) |
| Doğrudan Uzlaşma (Hakemsiz) Oranı | 13/16 (%81.25) | 13/16 (%81.25) | 10/16 (%62.50) | 36/48 (%75.00) |
| **Hibrit Mimari Nihai Doğruluğu** | **16/16 (%100.0)** | **16/16 (%100.0)** | **16/16 (%100.0)** | **48/48 (%100.0)** |

<div class="page-break"></div>

## 3. Vaka İncelemeleri

"""
    for domain in DOMAINS:
        md += f"### {domain['name']} Alanı Vakaları\n\n"
        
        # Load data
        original_data = load_jsonl(domain['data_file'])
        results_data = load_jsonl(domain['results_file'])
        
        # Create lookups
        context_map = {item['id']: item.get('context', 'Bağlam bulunamadı.') for item in original_data}
        question_map = {item['id']: item.get('question', 'Soru bulunamadı.') for item in original_data}
        
        for res in results_data:
            c_id = res['id']
            context = context_map.get(c_id, "Bağlam bulunamadı.")
            question = question_map.get(c_id, "Soru bulunamadı.")
            claim = res.get('claim', '')
            gold = res.get('gold_label', '')
            k1 = res.get('k1_pred', '')
            k2 = res.get('k2_pred', '')
            final = res.get('final_pred', '')
            reasoning = res.get('reasoning', '')
            correct = "✅ DOĞRU" if res.get('final_correct', False) else "❌ YANLIŞ"
            
            md += f"#### Vaka: `{c_id}`\n\n"
            md += f"**Bağlam:** {context}\n\n"
            md += f"**Soru:** {question}\n\n"
            md += f"**İddia (Sistem Çıktısı):** {claim}\n\n"
            
            md += f"| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |\n"
            md += f"| :--- | :--- | :--- | :--- | :--- |\n"
            md += f"| `{gold}` | `{k1}` | `{k2}` | `{final}` | **{correct}** |\n\n"
            
            md += f"**Hakem / Uzlaşma Gerekçesi:** {reasoning}\n\n"
            md += "---\n\n"
            
        md += "<div class=\"page-break\"></div>\n\n"
        
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(md)
    return md

def convert_md_to_html(md_text):
    html_body = markdown.markdown(md_text, extensions=['tables'])
    
    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 20mm;
        }}
        @media print {{
            .page-break {{ page-break-before: always; }}
            h4 {{ page-break-after: avoid; }}
            table {{ page-break-inside: avoid; }}
        }}
        body {{
            font-family: 'Times New Roman', Times, serif;
            line-height: 1.4;
            color: #000;
            font-size: 11pt;
            text-align: justify;
        }}
        h1, h2, h3, h4 {{
            font-family: Arial, sans-serif;
            color: #000;
        }}
        h1 {{ font-size: 18pt; text-align: center; border-bottom: 1px solid #000; padding-bottom: 10px; margin-bottom: 30px; }}
        h2 {{ font-size: 14pt; margin-top: 30px; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
        h3 {{ font-size: 13pt; margin-top: 25px; }}
        h4 {{ font-size: 11pt; margin-top: 20px; font-weight: bold; background-color: #f0f0f0; padding: 5px; border-left: 3px solid #666; }}
        p {{ margin-bottom: 10px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
            font-size: 10pt;
            font-family: Arial, sans-serif;
        }}
        th, td {{
            border: 1px solid #000;
            padding: 6px;
            text-align: left;
        }}
        th {{
            background-color: #e6e6e6;
            font-weight: bold;
        }}
        code {{
            font-family: 'Courier New', Courier, monospace;
            background-color: #f9f9f9;
            padding: 1px 3px;
            border: 1px solid #ddd;
            font-size: 9.5pt;
        }}
        hr {{ border: 0; border-top: 1px solid #ccc; margin: 20px 0; }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    return html

def render_pdf_with_chrome():
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={OUTPUT_PDF}",
        f"file:///{OUTPUT_HTML.replace(chr(92), '/')}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPORTS_DIR)
    if result.returncode == 0:
        print("PDF created at:", OUTPUT_PDF)
    else:
        print("Error:", result.stderr)

if __name__ == "__main__":
    md = generate_markdown()
    convert_md_to_html(md)
    render_pdf_with_chrome()
