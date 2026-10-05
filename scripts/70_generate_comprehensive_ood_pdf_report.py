import os
import re
import markdown

REPORTS_DIR = r"C:\Users\Engin Dalga\Documents\GitHub\halusinasyon\hls_new\k2_nli\reports"
OUTPUT_MD = os.path.join(REPORTS_DIR, "COMPREHENSIVE_OOD_EVALUATION_REPORT.md")
OUTPUT_HTML = os.path.join(REPORTS_DIR, "COMPREHENSIVE_OOD_EVALUATION_REPORT.html")

FILES_TO_MERGE = [
    "OOD_ALZHEIMER_CASE_STUDY_REPORT.md",
    "OOD_LEGAL_CASE_STUDY_REPORT.md",
    "OOD_FINANCE_CASE_STUDY_REPORT.md"
]

def generate_combined_markdown():
    combined_md = """# Dağılım Dışı (OOD) Veri Kümelerinde Kademeli Hibrit Mimarinin Kapsamlı Değerlendirme Raporu

**Tarih:** 5 Ekim 2026  
**Yazar:** Engin Dalga  
**Danışman:** Prof. Dr. Serkan Ballı  
**Tez Başlığı:** *Metin Tabanlı Türkçe Doğal Dil İşleme Veri Kümelerinde Halüsinasyon Tespiti ve Genellenebilirlik Analizi*  

## 1. Giriş ve Araştırma Motivasyonu
Bu rapor, geliştirilen Kademeli Hibrit Mimarinin ezber yapmadığını ve dağılım dışı (Out-of-Distribution - OOD) terminolojilerde de kararlı ve genellenebilir bir performans sergilediğini kanıtlamak amacıyla hazırlanmıştır. TR-FactBench eğitim kümesinde (%0 veri sızıntısı ile) tamamen bulunmayan üç zorlu alanda (Tıp/Alzheimer, Hukuk/İş Kanunu, Finans/Eurobond) toplam 48 kurgusal ve karmaşık vaka üzerinde yapılan detaylı incelemeler bu raporda bir araya getirilmiştir. 

### Kümülatif Başarı Tablosu (48 OOD Vakası):
- **K1 Başarısı (ELECTRA-TR):** 44/48 (%91.67)
- **K2 Başarısı (Gemma-4 + mDeBERTa):** 39/48 (%81.25)
- **Tam Hibrit Mimari Başarısı:** 48/48 (%100.0)
- **Doğrudan Yerel Uzlaşma Oranı:** 36/48 (%75.0) -> %75 API maliyeti tasarrufu.

Aşağıda her üç alana ait detaylı test raporları ve vaka incelemeleri (vaka vaka model yanıtları ve hakem kararları) sırasıyla sunulmaktadır.

<div style="page-break-after: always;"></div>

"""
    
    for filename in FILES_TO_MERGE:
        filepath = os.path.join(REPORTS_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                content = re.sub(r'^# ', r'## ', content, flags=re.MULTILINE)
                content = re.sub(r'^## ', r'### ', content, flags=re.MULTILINE)
                content = re.sub(r'^### ', r'#### ', content, flags=re.MULTILINE)
                combined_md += content + "\n\n<div style=\"page-break-after: always;\"></div>\n\n"
        else:
            print(f"Warning: {filename} not found.")

    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(combined_md)
    
    return combined_md

def convert_md_to_html(markdown_text):
    html_content = markdown.markdown(markdown_text, extensions=['tables', 'fenced_code'])
    
    full_html = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <style>
            @media print {{
                .page-break {{ page-break-before: always; }}
            }}
            body {{
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.5;
                color: #333;
                font-size: 11pt;
                max-width: 900px;
                margin: 0 auto;
                padding: 40px;
            }}
            h1 {{ color: #2c3e50; font-size: 22pt; text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-bottom: 30px; }}
            h2 {{ color: #2980b9; font-size: 16pt; margin-top: 30px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }}
            h3 {{ color: #16a085; font-size: 14pt; margin-top: 25px; }}
            h4 {{ color: #8e44ad; font-size: 12pt; margin-top: 20px; }}
            p {{ margin-bottom: 15px; text-align: justify; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                font-size: 10pt;
            }}
            th, td {{
                border: 1px solid #bdc3c7;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #ecf0f1;
                color: #2c3e50;
                font-weight: bold;
            }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            code {{
                background-color: #f4f6f7;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9.5pt;
                color: #c0392b;
            }}
            pre {{
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 10px;
                overflow-x: auto;
            }}
            pre code {{
                display: block;
                padding: 0;
                background-color: transparent;
                border: none;
                color: #333;
            }}
            blockquote {{
                border-left: 4px solid #2980b9;
                background-color: #f4f6f7;
                padding: 10px 15px;
                margin: 15px 0;
                color: #555;
                font-style: italic;
            }}
            ul, ol {{ margin-bottom: 15px; padding-left: 25px; }}
            li {{ margin-bottom: 5px; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"HTML generated successfully at {OUTPUT_HTML}")

if __name__ == "__main__":
    combined_md = generate_combined_markdown()
    print("Combined markdown generated.")
    convert_md_to_html(combined_md)
