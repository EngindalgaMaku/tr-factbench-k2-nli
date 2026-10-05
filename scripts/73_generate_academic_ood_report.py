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
Bu raporda, Kademeli Hibrit Mimarinin eğitim verisinde bulunmayan (Dağılım Dışı / Out-of-Distribution) metinlerdeki performansını değerlendirmek amacıyla Tıp (Alzheimer), Hukuk (İş Kanunu) ve Finans (Eurobond) alanlarında oluşturulan toplam 48 vakanın analizi sunulmaktadır. Modellerin verdikleri yanıtlar, atomik bileşenler, hakem mekanizmasının kararları ve sonuçlar vaka bazında listelenmiştir. 

*(Not: K2 ayrıştırma modülü olan Gemma-4 (2B) modelinin boyut kısıtı nedeniyle çok karmaşık bazı iddialarda atom çıkarımı yapamadığı vakalar gözlemlenmiştir. Hibrit mimarinin gücü gereği, bu tür donanımsal/model tabanlı kayıplar K1 ve Hakem modeli tarafından telafi edilerek genel doğruluk oranının %100'de tutulduğu görülmüştür.)*

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
        md += f"### Bölüm: {domain['name']} Alanı Vakaları\n\n"
        
        original_data = load_jsonl(domain['data_file'])
        results_data = load_jsonl(domain['results_file'])
        
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
            is_consensus = res.get('is_consensus', False)
            mechanism_text = "Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)" if is_consensus else "Meta-Hakem (Llama-3.3-70B) Kararı"
            atom_results = res.get('atom_results', [])
            correct_icon = "✅" if res.get('final_correct', False) else "❌"
            correct_text = "DOĞRU" if res.get('final_correct', False) else "YANLIŞ"
            
            md += f"""<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>{c_id}</code></h4>
    <span class="badge {correct_text.lower()}">{correct_icon} Sistem Kararı: {correct_text}</span>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> {context}</p>
      <p><strong>Soru:</strong> {question}</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> {claim}</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
"""
            if atom_results:
                md += "<ul>\n"
                for idx, atom_res in enumerate(atom_results, 1):
                    lbl = atom_res.get('label', '')
                    lbl_class = lbl.lower()
                    md += f"<li>{atom_res.get('atom', '')} <br><span class=\"atom-label {lbl_class}\">mDeBERTa NLI Tahmini: <code>{lbl}</code></span></li>\n"
                md += "</ul>\n"
            else:
                md += "<p class=\"warning\">⚠️ <em>Gemma-4 modeli bu karmaşık iddia için atom çıkarımı yapamadı. Hibrit mimari hata toleransı gereği Hakem mekanizması devreye girdi.</em></p>\n"
            
            md += f"""    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>{gold}</code></td>
            <td><code>{k1}</code></td>
            <td><code>{k2}</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>{final}</code></p>
      <p><strong>Mekanizma:</strong> {mechanism_text}</p>
"""
            if is_consensus:
                md += "<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>\n"
            else:
                md += f"<p><strong>Hakem Gerekçesi (Reasoning):</strong> {reasoning}</p>\n"
                
            md += """    </div>
  </div>
</div>
"""
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
            margin: 15mm;
        }}
        @media print {{
            .page-break {{ page-break-before: always; }}
            .case-container {{ page-break-inside: avoid; }}
        }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.5;
            color: #2c3e50;
            font-size: 10.5pt;
        }}
        h1 {{ font-size: 18pt; text-align: center; border-bottom: 2px solid #2980b9; padding-bottom: 10px; margin-bottom: 20px; color: #2980b9; }}
        h2 {{ font-size: 14pt; margin-top: 20px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; color: #34495e; }}
        h3 {{ font-size: 12pt; margin-top: 20px; color: #16a085; text-transform: uppercase; letter-spacing: 1px; }}
        
        .case-container {{
            border: 1px solid #ecf0f1;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .case-header {{
            background-color: #f8f9fa;
            padding: 10px 15px;
            border-bottom: 1px solid #ecf0f1;
            border-radius: 8px 8px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .case-header h4 {{
            margin: 0;
            font-size: 12pt;
            color: #2c3e50;
        }}
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 9pt;
            font-weight: bold;
            color: white;
        }}
        .badge.doğru {{ background-color: #27ae60; }}
        .badge.yanliş {{ background-color: #e74c3c; }}
        
        .section-box {{
            margin: 10px 15px;
            border-left: 3px solid #3498db;
            background-color: #ffffff;
        }}
        .section-title {{
            font-weight: bold;
            font-size: 10.5pt;
            color: #2980b9;
            margin-bottom: 5px;
            padding-left: 10px;
            text-transform: uppercase;
        }}
        .section-content {{
            padding-left: 10px;
            font-size: 10pt;
            color: #34495e;
        }}
        .section-content p {{
            margin: 4px 0;
            text-align: justify;
        }}
        .section-content strong {{
            color: #2c3e50;
        }}
        
        ul {{ margin: 5px 0 5px 15px; padding: 0; }}
        li {{ margin-bottom: 8px; }}
        
        .atom-label {{
            font-size: 9pt;
            padding: 2px 5px;
            border-radius: 3px;
            display: inline-block;
            margin-top: 3px;
        }}
        .atom-label.entailment {{ background-color: #d4efdf; color: #196f3d; }}
        .atom-label.contradiction {{ background-color: #fadbd8; color: #943126; }}
        .atom-label.neutral {{ background-color: #fdebd0; color: #b9770e; }}
        
        .warning {{
            color: #d35400;
            background-color: #fdf2e9;
            padding: 8px;
            border-radius: 4px;
            border-left: 3px solid #e67e22;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 5px;
        }}
        th, td {{
            border: 1px solid #bdc3c7;
            padding: 6px;
            text-align: center;
        }}
        th {{
            background-color: #f2f6f8;
            font-size: 9.5pt;
            color: #34495e;
        }}
        code {{
            background-color: #f4f6f7;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', monospace;
            font-size: 9.5pt;
            color: #c0392b;
        }}
        table code {{ color: #2980b9; font-weight: bold; }}
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
