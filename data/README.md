# Veri Şemaları

## Claim-level kayıt

Zorunlu alanlar: `example_id`, `context_id`, `domain`, `context`, `question`, `claim`, `gold_label`.

## Atomizer çıktı kaydı

K2 atomizeri çalıştırmaz. Harici atomizer aşağıdaki şemada sürümlenmiş çıktı üretmelidir:

```json
{
  "example_id": "legal_stress_0001",
  "claim_hash": "sha256-of-original-claim",
  "atomizer_version": "gemma_atomizer_v1",
  "checkpoint_hash": "...",
  "generation_config": {"do_sample": false},
  "atoms": [
    "Bireysel başvuru önceki yargılama giderlerinin iadesini sağlar.",
    "Kabul edilen dosyalar duruşmalı olarak incelenir."
  ]
}
```

`claim_hash`, atomların doğru claim sürümüyle eşleştiğini doğrulamak için kullanılır.
