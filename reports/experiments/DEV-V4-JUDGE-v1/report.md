# Frozen V4 judge on DEV disagreements

| Set | n | judge correct | judge acc | K1 right | K2 right | oracle | judge on K1-right / K2-right / both-wrong |
|---|---:|---:|---:|---:|---:|---:|---|
| dev960 | 219 | 193 | 0.8813 | 147 | 57 | 204 | 134/147 / 53/57 / 6/15 |
| dev600 | 139 | 128 | 0.9209 | 76 | 56 | 132 | 70/76 / 54/56 / 4/7 |
| gold480_reference | 123 | 110 | 0.8943 | 62 | 49 | 111 | 56/62 / 47/49 / 7/12 |
| dev_union | 358 | 321 | 0.8966 | 223 | 113 | 336 | 204/223 / 107/113 / 10/22 |

dev960: P0 acc 0.9469 vs K1 acc 0.899; judge vs K1 on disagreements {'only_first': 59, 'only_second': 13, 'p_exact': 0.0}

dev600: P0 acc 0.9517 vs K1 acc 0.865; judge vs K1 on disagreements {'only_first': 58, 'only_second': 6, 'p_exact': 0.0}

Usage: {'calls': 358, 'cost_usd': 0.1422, 'providers': {'DeepInfra': 7, 'Parasail': 2, 'Novita': 2, 'AkashML': 347}, 'finish_length': 0, 'parse_notes': {}}
