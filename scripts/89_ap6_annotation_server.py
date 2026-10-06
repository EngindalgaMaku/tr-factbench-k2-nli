#!/usr/bin/env python3
"""
89_ap6_annotation_server.py
Local, dependency-free annotation UI for AP6 (Python standard library only).

  python scripts/89_ap6_annotation_server.py --annotator A [--port 7870]

Reads  data/ap6/annotation/items_<annotator>.jsonl   (built by 88_ap6_build_annotation_set.py)
Writes data/ap6/annotation/labels_<annotator>.jsonl  (append-only; latest record per item wins)

Blinding: no system prediction and no automatic abstention flag is ever sent to
the browser. Items are pre-shuffled per annotator.
"""
from __future__ import annotations

import argparse
import json
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANN = ROOT / "data" / "ap6" / "annotation"
LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
ERROR_TYPES = ["relation_fabrication", "number_date", "scope", "negation", "added_information", "other"]
VISIBLE_FIELDS = ("item_id", "question", "answer_before", "sentence", "answer_after", "context", "domain")
LOCK = threading.Lock()

PAGE = r"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AP6 Etiketleme</title>
<style>
:root{--bg:#f7f7f5;--card:#fff;--ink:#1d1d1b;--muted:#6b6b66;--line:#e2e2dc;--accent:#2f5d8a;--hl:#fff1b8;--ok:#2e7d4f}
@media (prefers-color-scheme: dark){:root{--bg:#161616;--card:#1f1f1f;--ink:#ececea;--muted:#a3a39d;--line:#333;--accent:#7fb0e0;--hl:#5a4a10;--ok:#6cc596}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
header{display:flex;gap:16px;align-items:center;justify-content:space-between;padding:12px 20px;border-bottom:1px solid var(--line);background:var(--card);position:sticky;top:0;z-index:2}
header b{font-size:16px}#progress{color:var(--muted)}
main{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;padding:16px 20px;max-width:1500px;margin:auto}
@media(max-width:900px){main{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
h3{margin:0 0 8px;font-size:13px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
#context{white-space:pre-wrap;max-height:62vh;overflow:auto}
mark{background:var(--hl);color:inherit;padding:1px 2px;border-radius:3px}
.q{font-weight:600;margin-bottom:10px}
.btns{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 12px}
button{font:inherit;padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);cursor:pointer}
button.sel{border-color:var(--accent);outline:2px solid var(--accent)}
button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
.row{margin:10px 0}label.small{color:var(--muted);font-size:13px;display:block;margin-bottom:4px}
textarea{width:100%;min-height:54px;font:inherit;padding:8px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}
#status{color:var(--ok);font-size:13px;min-height:18px}.hint{color:var(--muted);font-size:12px}
</style></head><body>
<header><b>AP6 Etiketleme — Anotatör <span id="ann"></span></b><span id="progress"></span>
<span><button id="prev">← Önceki</button> <button id="next">Sonraki →</button> <button id="nextOpen">İlk boş madde</button></span></header>
<main>
<section class="card"><h3>Soru ve LLM yanıtı (hedef cümle vurgulu)</h3><div class="q" id="question"></div><div id="answer"></div>
<div class="row"><h3>Hedef cümle</h3><div id="sentence"></div></div></section>
<section class="card"><h3>Bağlam (LLM'e verilen kaynak parçalar)</h3><div id="context"></div></section>
<section class="card" style="grid-column:1/-1">
<div class="row"><label class="small">1) Bu cümle yalnızca kaynakta bir bilginin bulunmadığını mı söylüyor? (çekimser cümle)</label>
<div class="btns" id="abst"><button data-v="yes">Evet — çekimser</button><button data-v="no">Hayır — bilgi veren cümle</button></div></div>
<div class="row" id="labelRow"><label class="small">2) Etiket (klavye: 1–4) — cümlenin söyledikleri, bağlama göre:</label>
<div class="btns" id="label"><button data-v="supported">1 · supported</button><button data-v="partially_supported">2 · partially_supported</button><button data-v="contradicted">3 · contradicted</button><button data-v="unverifiable">4 · unverifiable</button></div></div>
<div class="row" id="errRow"><label class="small">3) Hata türü (supported değilse)</label>
<div class="btns" id="err"><button data-v="relation_fabrication">ilişki uydurma</button><button data-v="number_date">sayı / tarih</button><button data-v="scope">kapsam</button><button data-v="negation">olumsuzluk</button><button data-v="added_information">bilgi ekleme</button><button data-v="other">diğer</button></div></div>
<div class="row"><label class="small">Not (isteğe bağlı)</label><textarea id="note"></textarea></div>
<button class="primary" id="save">Kaydet ve sonraki (Enter)</button> <span id="status"></span>
<p class="hint">Göndermeleri ("bu hak", "bu süre") yanıtın geri kalanına göre çözün. Çekimser cümleler için etiket gerekmez. Etiketler anında diske yazılır.</p>
</section></main>
<script>
let items=[],labels={},idx=0,cur={};
const $=s=>document.querySelector(s);
const esc=s=>(s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
function pick(group,v){cur[group]=v;document.querySelectorAll('#'+group+' button').forEach(b=>b.classList.toggle('sel',b.dataset.v===v));refresh();}
function refresh(){const ab=cur.abst==='yes';$('#labelRow').style.opacity=ab?.35:1;$('#errRow').style.display=(!ab&&cur.label&&cur.label!=='supported')?'':'none';}
function show(){const it=items[idx];if(!it)return;
 $('#question').textContent=it.question;
 $('#answer').innerHTML=esc(it.answer_before)+' <mark>'+esc(it.sentence)+'</mark> '+esc(it.answer_after);
 $('#sentence').textContent=it.sentence;$('#context').textContent=it.context;
 const l=labels[it.item_id]||{};cur={abst:l.abstention,label:l.label,err:l.error_type};
 ['abst','label','err'].forEach(g=>document.querySelectorAll('#'+g+' button').forEach(b=>b.classList.toggle('sel',b.dataset.v===cur[g])));
 $('#note').value=l.note||'';refresh();
 const n=Object.keys(labels).length;$('#progress').textContent=`Madde ${idx+1} / ${items.length} · tamamlanan ${n}`;$('#status').textContent='';}
async function save(){const it=items[idx];
 if(!cur.abst){$('#status').textContent='Önce 1. soruyu cevaplayın.';return;}
 if(cur.abst==='no'&&!cur.label){$('#status').textContent='Etiket seçin.';return;}
 if(cur.abst==='no'&&cur.label!=='supported'&&!cur.err){$('#status').textContent='Hata türü seçin.';return;}
 const rec={item_id:it.item_id,abstention:cur.abst,label:cur.abst==='yes'?null:cur.label,error_type:(cur.abst==='no'&&cur.label!=='supported')?cur.err:null,note:$('#note').value};
 const r=await fetch('/api/label',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(rec)});
 if(r.ok){labels[it.item_id]=rec;$('#status').textContent='Kaydedildi ✓';if(idx<items.length-1){idx++;show();}}else{$('#status').textContent='Kayıt hatası!';}}
document.querySelectorAll('#abst button').forEach(b=>b.onclick=()=>pick('abst',b.dataset.v));
document.querySelectorAll('#label button').forEach(b=>b.onclick=()=>pick('label',b.dataset.v));
document.querySelectorAll('#err button').forEach(b=>b.onclick=()=>pick('err',b.dataset.v));
$('#save').onclick=save;$('#prev').onclick=()=>{if(idx>0){idx--;show();}};$('#next').onclick=()=>{if(idx<items.length-1){idx++;show();}};
$('#nextOpen').onclick=()=>{const j=items.findIndex(i=>!labels[i.item_id]);if(j>=0){idx=j;show();}};
document.addEventListener('keydown',e=>{if(e.target.tagName==='TEXTAREA')return;
 const m={'1':'supported','2':'partially_supported','3':'contradicted','4':'unverifiable'};
 if(m[e.key]){if(!cur.abst)pick('abst','no');pick('label',m[e.key]);}
 if(e.key==='Enter'){e.preventDefault();save();}if(e.key==='ArrowRight')$('#next').click();if(e.key==='ArrowLeft')$('#prev').click();});
(async()=>{const d=await (await fetch('/api/state')).json();items=d.items;labels=d.labels;$('#ann').textContent=d.annotator;
 const j=items.findIndex(i=>!labels[i.item_id]);idx=j>=0?j:0;show();})();
</script></body></html>"""


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def make_handler(annotator: str):
    items_path = ANN / f"items_{annotator}.jsonl"
    labels_path = ANN / f"labels_{annotator}.jsonl"
    items = [{k: it.get(k, "") for k in VISIBLE_FIELDS} for it in read_jsonl(items_path)]
    item_ids = {it["item_id"] for it in items}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep the console quiet
            pass

        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                return self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            if self.path == "/api/state":
                latest = {}
                for rec in read_jsonl(labels_path):
                    latest[rec["item_id"]] = rec
                payload = {"annotator": annotator, "items": items, "labels": latest}
                return self._send(200, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json")
            return self._send(404, b"not found", "text/plain")

        def do_POST(self):
            if self.path != "/api/label":
                return self._send(404, b"not found", "text/plain")
            rec = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode("utf-8"))
            ok = (rec.get("item_id") in item_ids and rec.get("abstention") in ("yes", "no")
                  and (rec["abstention"] == "yes" or rec.get("label") in LABELS)
                  and (rec.get("error_type") is None or rec["error_type"] in ERROR_TYPES))
            if not ok:
                return self._send(400, b"invalid record", "text/plain")
            rec["annotator"] = annotator
            rec["saved_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            with LOCK, labels_path.open("a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            return self._send(200, b"ok", "text/plain")

    return Handler, len(items)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--annotator", required=True, choices=["A", "B", "DEMO"])
    ap.add_argument("--port", type=int, default=7870)
    args = ap.parse_args()
    handler, n = make_handler(args.annotator)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Annotator {args.annotator}: {n} items -> http://127.0.0.1:{args.port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
