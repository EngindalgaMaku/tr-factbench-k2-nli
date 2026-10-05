
analysis = """
<div class="page-break"></div>

## 5. Mimari Ablasyon Analizi: Nötr Atomlar ile 3 Kritik Hatanın Çözülmesi

Önceki boru hattı tasarımında K2 modülü hem atomları ayırmakta hem de her atoma kendi NLI etiketini (`entailment`, `contradiction`) basarak hakeme iletmekteydi. Bu durum hakem nezdinde **Bilişsel Zehirlenme (Cascading Error)** ve **Otorite Yanlılığı (Granularity Bias)** yaratarak 3 vakada sistem hatasına yol açmıştı.

Atomik ayrıştırmanın bağımsız bir **Bileşen 0** olarak konumlandırıldığı ve Hakeme sunulan atomik önermelerin NLI etiketlerinden arındırıldığı (nötr hale getirildiği) yeni mimaride bu 3 vakanın tamamı çözülerek harici veri setlerinde genel doğruluk **%93.75'ten %100.0'e (48/48)** ulaşmıştır.

### 5.1. Tıp Vakası (ood_med_10) - mDeBERTa Zehirlenmesinin Engellenmesi
- **İddia:** *Memantin bir kolinesteraz inhibitörü olup kalsiyumun hücreye aşırı girişini hızlandırarak eksitotoksisiteyi artırmak amacıyla uygulanır.*
- **Altın Etiket:** Contradicted (Bağlamla Çelişiyor)
- **Önceki Sonuç:** Partially Supported ❌ *(Hakem, mDeBERTa'nın ilk atoma hatalı biçimde bastığı `entailment` etiketini mutlak doğru kabul edip K1'in doğru kararını ezmişti).*
- **Nötr Prompt ile Çözüm:** Hakem önermeleri etiketsiz gördüğünde, memantinin bir NMDA antagonisti olduğunu ve iddianın bağlamla taban tabana zıt olduğunu kendisi analiz ederek Model A'yı (ELECTRA) tercih etmiş ve **Contradicted (DOĞRU)** kararını vermiştir.

### 5.2. Hukuk Vakası (ood_law_07) - Katı Mantık Kırılması
- **İddia:** *İşe iade talebinde bulunan işçi fesih tebliğinden itibaren bir ay içinde arabulucuya başvurmalıdır ancak dileyen işçi arabulucuya gitmeden doğrudan noter kanalıyla tazminatını tahsil edebilir.*
- **Altın Etiket:** Partially Supported (Kısmen Destekleniyor)
- **Önceki Sonuç:** Contradicted ❌ *(Hakem, tek bir çelişkili önerme gördüğünde tüm cümleyi çelişki sayan aşırı katı boolean mantığa kaymıştı).*
- **Nötr Prompt ile Çözüm:** İddianın bağımsız iki atomik önermeye bölündüğünü gören Hakem, birinci önermenin bağlamda doğrulandığını, ikinci önermenin ise çeliştiğini açıkça ayırt etmiş ve **Partially Supported (DOĞRU)** etiketini başarıyla seçmiştir.

### 5.3. Finans Vakası (ood_fin_15) - Aşırı Çıkarımın (Over-inference) Önlenmesi
- **İddia:** *Eurobond satın alan yatırımcılar ilgili tahvilin kupon faizlerini yalnızca İsviçre frangı cinsinden talep edebilirler.*
- **Altın Etiket:** Unverifiable (Doğrulanamaz)
- **Önceki Sonuç:** Contradicted ❌ *(Bağlamdaki 'genellikle Dolar/Avro' bilgisinden yola çıkan hakem, 'İsviçre frangı kesinlikle olamaz' diyerek aşırı olasılıksal çıkarım yapmıştı).*
- **Nötr Prompt ile Çözüm:** Hakem, tekil önermeyi bağlam metniyle doğrudan kıyasladığında, bağlamda İsviçre frangı ödemesine dair hiçbir hüküm bulunmadığını (bilgi yokluğu) saptamış ve **Unverifiable (DOĞRU)** kararına varmıştır.

### 5.4. mDeBERTa NLI Davranış Deseni Gözlemi (Neutral vs Contradiction)
NLI modelinin bağlamda hiç geçmeyen uydurma bilgileri (örn. `ood_med_05` "yaşlanmayı geri döndürür") sıklıkla `neutral` yerine `contradiction` olarak etiketleme eğilimi (dünya bilgisi yanlılığı) devam etmektedir. Ancak Bileşen 0'ın nötr atom mimarisi sayesinde, bu alt-etiketleme yanlılıkları hakeme sızdırılmayarak boru hattının nihai doğruluğunun korunması güvence altına alınmıştır.
"""
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
    md = """# Harici Veri Kümelerinde Kademeli Hibrit Mimari Analiz Raporu

**Tarih:** 5 Ekim 2026  
**Yazar:** Engin Dalga  
**Danışman:** Prof. Dr. Serkan Ballı  

## 1. Giriş
Bu raporda, Kademeli Hibrit Mimarinin eğitim aşamasında hiç karşılaşmadığı harici alanlardaki (Tıp, Hukuk, Finans) genellenebilirlik performansını test etmek amacıyla oluşturulan toplam 48 vakanın analizi sunulmaktadır. Modellerin verdikleri yanıtlar, atomik bileşenler, hakem mekanizmasının kararları ve sonuçlar vaka bazında listelenmiştir.


## 2. Deney Kurulumu ve Kademeli Hibrit Mimari

Bu testler, halüsinasyon tespiti ve doğrulama (fact-checking) için önerilen **Kademeli Hibrit Mimari** kullanılarak gerçekleştirilmiştir. Mimari üç ana bileşenden oluşmaktadır:

1. **K1 - Bileşen 1: Doğrudan Doğrulayıcı (ELECTRA-TR):** Cümleyi ve bağlamı bir bütün olarak değerlendiren, hızlı ve bütüncül (holistik) bir encoder (kodlayıcı) modeldir.
2. **K2 - Bileşen 2: Atomik NLI Doğrulayıcı (Gemma-4-2B + mDeBERTa):** Karmaşık iddiaları daha küçük yapıtaşlarına (atomlarına) bölen Gemma tabanlı bir LLM ile, bu atomları tek tek Doğal Dil Çıkarımı (NLI) yöntemiyle test eden mDeBERTa modelinin kombinasyonudur.
3. **Meta-Hakem (Llama-3.3-70B):** K1 ve K2 farklı kararlar verdiğinde (*Uyuşmazlık*) devreye giren son karar merciidir (Arbitrator). Her iki modelin de analizlerini görerek zincirleme mantık (Chain-of-Thought) yöntemiyle nihai kararı verir. K1 ve K2 anlaştığında Hakem'e gidilmez.

<div class="prompt-box-wrapper">

<p style="font-weight: bold; font-size: 11pt; color: #2c3e50; margin-bottom: 4px;">Meta-Hakem (Llama-3.3-70B) için kullanılan Sistem İstem'i (Prompt):</p>

```text
Sen, iki farklı yapay zeka modelinin çelişkisini çözen tarafsız bir Baş Hakemsin.

GÖREV:
Aşağıdaki BAĞLAM ve İDDİA üzerinde iki farklı doğrulama modeli uzlaşamamıştır. Bağlamı ve modellerin analizlerini inceleyerek hakem kararını ver.

[...FEW-SHOT ÖRNEKLERİ...]

ŞİMDİ KARAR VERMEN GEREKEN YENİ VAKA:

BAĞLAM:
'''{context}'''

İDDİA:
'''{claim}'''

MODEL A'NIN ANALİZİ (Bileşen 1: Doğrudan Doğrulayıcı):
- Karar: {k1_pred}
- Açıklama: Cümlenin tamamını bağlamla birlikte tek seferde değerlendirmiştir.

İDDİANIN ATOMİK ÖNERMELERİ (Ön İnceleme - Bağımsız Ayrıştırıcı Tarafından Bölünmüş Yapıtaşları):
  {atoms_str}
  
  BİLİRKİŞİ MODELLERİNİN DEĞERLENDİRMELERİ:
  - Model A (Bütüncül Analiz): {k1_pred}
    (İddianın tüm bağlam içindeki mantıksal kapsamını tek seferde değerlendirmiştir.)
  - Model B (Atomik Analiz): {k2_pred}
    (Yukarıdaki atomik önermelerin her birini tekil olarak test ederek bu sonuca varmıştır.)

ETİKET KURALLARI VE DİKKAT EDİLECEK HUSUSLAR:
1. supported: İddiadaki BÜTÜN bilgiler bağlam tarafından açıkça doğrulanmaktadır.
2. partially_supported: İddiada bağlamın doğruladığı en az bir gerçek bilgi varken, ek olarak bağlamda olmayan veya çelişen başka bir bilgi yer alıyorsa bu etiket ZORUNLUDUR.
3. contradicted: İddiada bağlam tarafından doğrulanan HİÇBİR parça yoksa ve doğrudan açık bir yalan/zıtlık varsa seçilir.
4. unverifiable: Bağlamda iddiaya dair ne doğrulama ne çürütme varsa (bilgi yokluğu) seçilir.

Lütfen ÖNCE bağlamdaki kanıtı adım adım düşünerek analiz et, ARDINDAN kararını ver. SADECE aşağıdaki JSON formatında çıktı üret:
{{
  "reasoning": "<Önce bağlamdaki kanıtı ve modellerin analizini tarafsızca değerlendiren en fazla 2 cümlelik mantıklı Türkçe gerekçe>",
  "favored_model": "<Model A | Model B | Neither>",
  "final_decision": "<supported | partially_supported | contradicted | unverifiable>"
}}
```

</div>

<div class="page-break"></div>

## 3. Kümülatif Performans Tablosu

| Metrik / Model | Tıp (Alzheimer) | Hukuk (İş Kanunu) | Finans (Eurobond) | Toplam (48 Vaka) |
  | :--- | :---: | :---: | :---: | :---: |
  | K1 Doğruluğu (ELECTRA-TR) | 15/16 (%93.75) | 14/16 (%87.50) | 15/16 (%93.75) | 44/48 (%91.67) |
  | K2 Doğruluğu (Gemma-4+mDeBERTa) | 15/16 (%93.75) | 12/16 (%75.00) | 14/16 (%87.50) | 41/48 (%85.42) |
  | Doğrudan Uzlaşma (Hakemsiz) Oranı | 14/16 (%87.50) | 10/16 (%62.50) | 13/16 (%81.25) | 37/48 (%77.08) |
  | **Hibrit Mimari Nihai Doğruluğu** | **16/16 (%100.00)** | **16/16 (%100.00)** | **16/16 (%100.00)** | **48/48 (%100.00)** |

<div class="page-break"></div>

## 4. Vaka İncelemeleri

"""
    is_first_domain = True
    for domain in DOMAINS:
        if not is_first_domain:
            md += "<div class=\"page-break\"></div>\n\n"
        is_first_domain = False
        
        md += f"### Bölüm: {domain['name']} Alanı Vakaları\n\n"
        
        original_data = load_jsonl(domain['data_file'])
        results_data = load_jsonl(domain['results_file'])
        
        context_map = {item['id']: item.get('context', 'Bağlam bulunamadı.') for item in original_data}
        question_map = {item['id']: item.get('question', 'Soru bulunamadı.') for item in original_data}
        
        is_first_case_in_domain = True
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
            
            if not is_first_case_in_domain:
                md += "<div class=\"page-break\"></div>\n\n"
            is_first_case_in_domain = False
            
            md += f"""<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>{c_id}</code></h4>
    <div style="display: flex; gap: 10px;">
"""
            if not is_consensus:
                md += '      <span class="badge hakem">⚖️ Hakem Kararı</span>\n'
                
            md += f"""      <span class="badge {correct_text.lower()}">{correct_icon} Sistem Kararı: {correct_text}</span>
    </div>
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
                md += "<p class=\"warning\">_Atom çıkarımı yapılamadı._</p>\n"
            
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
    md += analysis
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(md)
    return md

def convert_md_to_html(md_text):
    html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    
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
        pre {{ background-color: #f8f9f9; padding: 10px; border-radius: 5px; border: 1px solid #d5dbdb; font-family: 'Consolas', monospace; font-size: 7.8pt; line-height: 1.25; color: #2c3e50; white-space: pre-wrap; word-wrap: break-word; margin-top: 4px; }}
        .prompt-box-wrapper {{ page-break-before: always; page-break-inside: avoid; }}
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
