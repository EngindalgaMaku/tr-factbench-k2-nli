# Component failure patterns on DEV (and Gold-480 for reference)

| Pattern | dev960: claims / K2 acc with / without / share of K2 errors | dev600: claims / K2 acc with / without / share of K2 errors | gold480: claims / K2 acc with / without / share of K2 errors |
|---|---|---|---|
| P1_undersplit_partial | 1 / 0.0 / 0.806 / 0.0053 | 0 / None / 0.8317 / 0.0 | 3 / 0.0 / 0.8092 / 0.0319 |
| P2_anaphoric_atom | 41 / 0.8537 / 0.803 / 0.0321 | 12 / 0.8333 / 0.8316 / 0.0198 | 28 / 0.8214 / 0.8031 / 0.0532 |
| P3_short_atom | 118 / 0.7288 / 0.8159 / 0.1711 | 36 / 0.8056 / 0.8333 / 0.0693 | 67 / 0.8507 / 0.7966 / 0.1064 |
| P4_weak_entailment | 54 / 0.3704 / 0.8311 / 0.1818 | 25 / 0.52 / 0.8452 / 0.1188 | 29 / 0.4138 / 0.8293 / 0.1809 |
| P5_subhalf_entailment | 6 / 0.5 / 0.8071 / 0.016 | 5 / 0.6 / 0.8336 / 0.0198 | 4 / 0.25 / 0.8088 / 0.0319 |

K1 restrictive adverb (with / without): dev960: pred-C rate 0.5211 / 0.2385, precision 0.8378 / 0.8632, n 71; dev600: pred-C rate 0.2222 / 0.2321, precision 1.0 / 0.9398, n 27; gold480: pred-C rate 0.3962 / 0.2412, precision 0.8095 / 0.7767, n 53

dev960 K2 error directions: partially_supported -> supported 36, contradicted -> partially_supported 34, supported -> partially_supported 23, contradicted -> supported 13, unverifiable -> contradicted 13, unverifiable -> supported 13
dev600 K2 error directions: contradicted -> partially_supported 33, supported -> partially_supported 21, unverifiable -> partially_supported 18, partially_supported -> supported 7, partially_supported -> contradicted 6, unverifiable -> contradicted 5
gold480 K2 error directions: partially_supported -> supported 18, contradicted -> partially_supported 17, unverifiable -> partially_supported 15, supported -> partially_supported 13, unverifiable -> supported 6, unverifiable -> contradicted 6
