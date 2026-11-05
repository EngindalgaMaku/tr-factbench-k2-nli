# Confidence routing selected on DEV (no API calls)

DEV disagreements: DEV960 219, DEV600 139.

| tau | union | DEV960 | DEV600 |
|---:|---:|---:|---:|
| 0.0 | 223 | 147 | 76 |
| 0.5 | 223 | 147 | 76 |
| 0.6 | 223 | 149 | 74 |
| 0.7 | 228 | 153 | 75 |
| 0.75 | 230 | 152 | 78 |
| 0.8 | 231 | 153 | 78 |
| 0.85 | 234 | 155 | 79 |
| 0.9 | 236 | 154 | 82 |
| 0.95 | 243 | 156 | 87 |
| 0.99 | 237 | 151 | 86 |
| 0.999 | 208 | 130 | 78 |
| 1.01 | 113 | 57 | 56 |

Selected tau = 0.95 (Gold disagreements below tau: 29/123)

| Gold-480 system | correct | acc | judge calls |
|---|---:|---:|---:|
| K1 | 399 | 0.8313 | 0 |
| L_tau | 408 | 0.85 | 0 |
| P0 | 447 | 0.9313 | 123 |
| P0_tau | 437 | 0.9104 | 94 |

McNemar L_tau vs K1: {'only_first_correct': 16, 'only_second_correct': 7, 'p_exact': 0.0931}
McNemar L_tau vs P0: {'only_first_correct': 5, 'only_second_correct': 44, 'p_exact': 0.0}
McNemar P0_tau vs P0: {'only_first_correct': 0, 'only_second_correct': 10, 'p_exact': 0.002}
