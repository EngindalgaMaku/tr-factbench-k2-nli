# PA rule on DEV (frozen rule, archived Gemma-4-26B zero-shot, no API calls)

## dev960 (n=960, Gemma matched 960, routed agreements 364, unmatched 0)
- acc: {'K1': 0.899, 'P0': 0.9469, 'PA': 0.9521, 'gemma_zero_shot_all': 0.9427}
- routed: agreed label correct 347/364, Gemma correct 352/364, fixed 10, broken 5
- PA vs P0: {'only_first': 10, 'only_second': 5, 'p_exact': 0.3018}; LLM call share {'P0': 0.2281, 'PA': 0.6073}
- by domain (fixed/broken): finance 2/3 of 119; legal 5/0 of 127; medical 3/2 of 118

## dev600 (n=600, Gemma matched 599, routed agreements 236, unmatched 0)
- acc: {'K1': 0.865, 'P0': 0.9517, 'PA': 0.97, 'gemma_zero_shot_all': 0.9633}
- routed: agreed label correct 221/236, Gemma correct 232/236, fixed 14, broken 3
- PA vs P0: {'only_first': 14, 'only_second': 3, 'p_exact': 0.0127}; LLM call share {'P0': 0.2317, 'PA': 0.625}
- by domain (fixed/broken): finance 6/1 of 79; legal 4/2 of 80; medical 4/0 of 77

