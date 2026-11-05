# DEV disagreement set (frozen K1, frozen atomizer + K2 soft-prob)

## dev960 (n=960, atomizer failures 0)

- K1 acc 0.899, Macro-F1 0.8994; K2 acc 0.8052, Macro-F1 0.806; oracle acc 0.9583
- Agreement 741 (errors 25: {'contradicted': 4, 'partially_supported': 13, 'supported': 6, 'unverifiable': 2})
- Disagreement 219: K1 right 147, K2 right 57, both wrong 15
- By K1 confidence: [0.00,0.80) n=27 K1 8 K2 14; [0.80,0.90) n=13 K1 5 K2 6; [0.90,0.99) n=43 K1 21 K2 18; [0.99,1.00) n=136 K1 113 K2 19
- By domain: finance n=76 K1 52 K2 20; legal n=60 K1 41 K2 18; medical n=83 K1 54 K2 19

## dev600 (n=600, atomizer failures 0)

- K1 acc 0.865, Macro-F1 0.8686; K2 acc 0.8317, Macro-F1 0.8364; oracle acc 0.9583
- Agreement 461 (errors 18: {'partially_supported': 15, 'unverifiable': 2, 'supported': 1})
- Disagreement 139: K1 right 76, K2 right 56, both wrong 7
- By K1 confidence: [0.00,0.80) n=16 K1 6 K2 8; [0.80,0.90) n=10 K1 3 K2 7; [0.90,0.99) n=37 K1 16 K2 20; [0.99,1.00) n=76 K1 51 K2 21
- By domain: finance n=47 K1 24 K2 20; legal n=43 K1 22 K2 19; medical n=49 K1 30 K2 17
