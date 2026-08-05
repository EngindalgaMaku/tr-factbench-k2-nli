# İlk Veri Denetimi

- dev_general: 960 örnek, 240 benzersiz context.
- dev_stress: 600 örnek, 150 benzersiz context.
- İki dosya arasında context_id, context metni, claim ve example_id çakışması yoktur.
- Her context dört claim içerir; insan re-annotasyonu sonrasında 5 context grubunda etiketler artık bire bir dört-sınıf dengesi göstermemektedir.
- Her iki veri seti de üç domain ve dört sınıfta yaklaşık dengelidir.
- Annotation status bütün satırlarda `single_annotator_provisional`dır.
- Stress dosyasındaki `atom_count` alanı 72 resmi kaynak replacement kaydında boştur; bu alan gold atom anotasyonu olarak kabul edilmez.
- Claim-level model selection için partially_supported dışarıda bırakılır.
- Atom-level verifier değerlendirmesi için 240 örneklik dengeli human annotation şablonu oluşturulmuştur.
