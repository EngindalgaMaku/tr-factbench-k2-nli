import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_id = "google/gemma-4-E2B-it"
tok = AutoTokenizer.from_pretrained(model_id, local_files_only=True)
quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=quant_config, device_map="cuda", local_files_only=True)

case = json.loads(open("data/processed/arbitration/arbitration_cases_120.jsonl", encoding="utf-8").readline())

atoms_str = "\n".join([f"- Atom {i+1}: \"{a['atom']}\" -> Sonuç: {a['label']}" for i, a in enumerate(case["k2_atoms"])])
prompt = f"""Sen, iki farklı yapay zeka modelinin çelişkisini çözen tarafsız bir Baş Hakemsin.

GÖREV:
Aşağıdaki BAĞLAM ve İDDİA üzerinde iki farklı model anlaşamamıştır. Bağlamı ve modellerin analizlerini inceleyerek hakem kararını ver.

BAĞLAM:
\"\"\"{case['context']}\"\"\"

İDDİA:
\"\"\"{case['claim']}\"\"\"

MODEL A'NIN ANALİZİ:
- Karar: {case['k1_pred']}

MODEL B'NİN ANALİZİ:
- Karar: {case['k2_pred']}
- Önermeler:
{atoms_str}

ETİKET TANIMLARI:
- supported: Bütün bilgiler bağlam tarafından açıkça desteklenmektedir.
- partially_supported: İddiada hem doğru/desteklenen hem de bağlamla çelişen/bağlamda olmayan bilgiler bir aradadır.
- contradicted: İddiada desteklenen hiçbir bilgi yoktur ve bağlamla doğrudan çelişmektedir.
- unverifiable: İddiadaki bilgi bağlamda hiç yer almamaktadır (bilgi yokluğu).

Lütfen tarafsız bir inceleme yap ve SADECE aşağıdaki JSON formatında çıktı üret:
```json
{{
  "reasoning": "<Hangi modelin neden haklı veya hatalı olduğunu bağlama göre açıklayan kısa Türkçe analiz>",
  "favored_model": "<Model A veya Model B veya Neither>",
  "final_decision": "<supported veya partially_supported veya contradicted veya unverifiable>"
}}
```"""

messages = [{"role": "user", "content": prompt}]
input_prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tok(input_prompt, return_tensors="pt").to(model.device)

out = model.generate(**inputs, max_new_tokens=180, temperature=0.1, do_sample=False)
raw = tok.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()

print("=" * 60)
print("HAKEMİN RAW ÇIKTISI:")
print(raw)
print("=" * 60)
print("MODEL A (K1):", case["k1_pred"])
print("MODEL B (K2):", case["k2_pred"])
print("GERÇEK ETİKET (GOLD):", case["gold_label"])
