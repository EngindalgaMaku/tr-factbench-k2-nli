# K1 shortcut flag on disagreements (no API)

S: no-context prediction = full prediction, full != unverifiable, no-context confidence >= 0.65

| Set | eligible | S: n / K1 error rate / judge acc / judge followed wrong K1 | not S: n / K1 error rate / judge acc / followed wrong K1 | Fisher OR, p |
|---|---:|---|---|---|
| dev_union | 311 | 69 / 0.261 / 0.899 / 3 | 242 / 0.45 / 0.893 / 6 | 0.431, 0.0053 |
| dev960 | 185 | 41 / 0.195 / 0.878 / 1 | 144 / 0.396 / 0.868 / 4 | 0.37, 0.0252 |
| dev600 | 126 | 28 / 0.357 / 0.929 / 2 | 98 / 0.531 / 0.929 / 2 | 0.491, 0.1345 |
| gold480_once | 110 | 7 / 0.286 / 0.857 / 0 | 103 / 0.544 / 0.893 / 4 | 0.336, 0.2519 |
