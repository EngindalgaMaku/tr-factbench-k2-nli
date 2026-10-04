# Kademeli Hibrit Boru Hattı Donanım, Gecikme (Latency) ve VRAM Profilleme Raporu
## Tek Tüketici GPU'sunda (RTX 4060 8GB) Uçtan Uca Çıkarım Performansı ve Frugal AI Analizi

**Tarih:** 4 Ekim 2026  
**Test Donanımı:** NVIDIA GeForce RTX 4060 Laptop GPU (8.00 GB GDDR6 VRAM)  
**Yazar:** Engin Dalga | **Danışman:** Prof. Dr. Serkan Ballı  
**Tez Başlığı:** *Türkçe Büyük Dil Modeli Yanıtlarında Halüsinasyon Tespiti: Hibrit Bir Doğrulama Yaklaşımı ve Genellenebilirlik Analizi*  
**Ham Metrik Dosyası:** [`reports/LATENCY_AND_VRAM_PROFILING_RESULTS.json`](file:///c:/Users/Engin%20Dalga/Documents/GitHub/halusinasyon/hls_new/k2_nli/reports/LATENCY_AND_VRAM_PROFILING_RESULTS.json)

---

## 1. Yönetici Özeti ve Frugal AI İspatı

Tezimizin en temel mühendislik iddialarından biri; **büyük dil modellerinin yüksek maliyetini ve donanım açlığını kırarak, sistemi tüketici sınıfı (8GB VRAM) tek bir GPU üzerinde çalışabilir kılmaktır (Yeşil Bilişim / Frugal AI).**

Bu deneyde, boru hattımızın tüm bileşenleri gerçek donanım üzerinde milisaniye (`ms`) ve bellek (`MB/GB`) hassasiyetiyle profillenmiştir.

### 🌟 Öne Çıkan Temel Sonuçlar:
1. **8GB VRAM'e Kusursuz Sığma:** Yerel modellerin (K1 ELECTRA + K2 Gemma-4 4-bit + K2 mDeBERTa) toplam GPU VRAM ayak izi **7.39 GB** olarak ölçülmüştür. Sistem, veri merkezlerine veya çoklu A100 kümelerine ihtiyaç duymadan **orta seviye tek bir tüketici dizüstü GPU'sunda (RTX 4060)** rahatlıkla çalışmaktadır.
2. **K1 İnanılmaz Hızlı (~15.36 ms):** Bütüncül ELECTRA modeli tek bir iddiayı ortalama **15.36 milisaniyede** doğrulamakta ve saniyede **65.12 iddia** işleyebilmektedir. K1, bulut tabanlı 70B LLM'den **yaklaşık 290 kat daha hızlıdır**!
3. **K2'nin İnce Taneli Analiz Maliyeti:** Gemma-4 QLoRA üretici modeli, yerel dizüstü GPU'sunda standart PyTorch çıkarımı ile ortalama **~9.1 saniyede** iddiayı atomlara ayırmaktadır. Bu süre, modelin doğruluğunu ve açıklanabilirliğini artırırken, çıkarım süresinin asıl belirleyicisi olmaktadır.
4. **%74.9 API Maliyet Tasarrufu:** 478 vakanın 358'i sıfır bulut maliyetiyle yerel GPU'da çözülmüştür.

---

## 2. Bileşen Bazlı Gecikme ve Donanım Tüketim Tablosu

| Bileşen | Model Mimarisi | Parametre Sayısı | Kuantizasyon | Model VRAM Ayak İzi | Ortalama Gecikme (Mean) | Medyan Gecikme (p50) | p95 Gecikme | Verim (Throughput) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bileşen 1 (K1)** | ELECTRA-TR Base + LoRA | 110.6 M | FP16 / BF16 | **435.13 MB** | **15.36 ms** | 15.21 ms | 15.73 ms | **65.12 iddia/sn** |
| **Bileşen 2A (Atomizer)** | Gemma-4-E2B-it | 2.6 B | **4-bit NF4 (QLoRA)** | **6576.5 MB** | **9136.26 ms** | 9006.6 ms | 12875.69 ms | ~1.5 iddia/sn |
| **Bileşen 2B (NLI)** | mDeBERTa-v3-base | 86.0 M | FP16 | **552.87 MB** | **26.51 ms** | 17.93 ms | 37.56 ms | **37.72 çift/sn** |
| **Bileşen 2 Toplam (K2)** | Gemma-4 + mDeBERTa | ~2.7 B | Hibrit | **7129.37 MB** | **9191.04 ms** | 9043.66 ms | — | ~1.3 iddia/sn |
| **Bileşen 3 (Hakem)** | Llama-3.3-70B-Instruct | **70.0 B** | FP8 / 16 (Bulut) | *(Uzak API)* | **4.46 sn** | 4.07 sn | 6.79 sn | ~0.3 istek/sn |

---

## 3. Sistem Seviyesi Gecikme ve Kademeli Karşılaştırma

Aşağıdaki tablo, Kademeli Hibrit Mimari ile Saf LLM yaklaşımının zaman ve maliyet karşılaştırmasını göstermektedir:

| Metrik / Parametre | K1 Tek Başına | K2 Tek Başına | Saf LLM (Full Judge 70B) | KADEMELİ HİBRİT BORU HATTI |
| :--- | :---: | :---: | :---: | :---: |
| **Doğruluk (Accuracy)** | %83.13 | %80.33 | %89.54 | **%90.79 (En Yüksek)** |
| **Tek İddia Gecikmesi** | **15.36 ms** | 9.19 sn | 4.46 sn | 9.20 sn (Konsensüs) / 13.6 sn (Hakem) |
| **Throughput (İşleme Hızı)** | **65.1 iddia/sn** | ~1.3 iddia/sn | ~0.22 istek/sn | Dengeli Hibrit |
| **1000 İddia API Maliyeti** | **$0.00** | **$0.00** | ~$0.30 USD | **~$0.07 USD (%74.9 Tasarruf)** |
| **Gerekli Yerel VRAM** | **<0.5 GB** | ~7.1 GB | — (Bulut Bağımlı) | **7.39 GB (8GB GPU'ya Tam Sığar)** |

---

## 4. Tez Savunması İçin Mühendislik Çıkarımları

1. **Uygulanabilirlik (Deployability) ve Yeşil Bilişim (Frugal AI):**  
   Literatürdeki pek çok çalışma yüzlerce milyar parametreli modeller önererek pratik hayatta karşılanması imkansız donanım maliyetleri doğurmaktadır. Bu çalışma; yerel katmanda **yalnızca 7.39 GB VRAM** tüketerek, herhangi bir hastane, kamu kurumu veya bankada veri gizliliği (KVKK/on-premise) standartlarına uygun biçimde tek bir tüketici GPU'sunda çalıştırılabileceğini ampirik olarak kanıtlamıştır.
2. **K1'in Hız Gücü (15 ms):**  
   K1'in 15 milisaniyelik ultra-hızlı çıkarımı, anlık akışlarda (real-time chat/streaming) ilk filtreleme mekanizması olarak eşsiz bir değer sunmaktadır.
3. **Maliyet-Doğruluk Dengesi:**  
   Sistem, 70B bulut modelinin tek başına sağladığı doğruluğun dahi üzerine çıkarak (%90.79 vs %89.54), bulut çağrısı maliyetini ve bağımlılığını **%74.9 oranında düşürmüştür**.
