# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/a5044673838-gif/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/a5044673838-gif/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A one-day world news infographic for make.fun's "Sum up 26 November's world
news in one image" bounty ($100 shared pot). The program draws a 1024x1024
PNG with six verified stories first reported on Thursday 26 November 2026:
North Korea expelling Switzerland's envoy, the first Pakistani astronaut
reaching China's Tiangong station aboard Shenzhou-24, Bangladesh's 36%
garment-worker pay rise, the Australia-Solomon Islands pact, the US
shelving a Russia business-deal peace plan (Financial Times reports), and
a record 1,220 registrations for the IPL 2027 auction. Every story was
checked against AFP, Reuters, the Financial Times, The Indian Express or
The Manila Times reporting; nothing is invented. Pure Python standard
library, no network, fully deterministic.

## Run it

```
python3 main.py
```

Writes `entry.png` to `/output` (`MAKEFUN_OUTPUT_DIR` overrides).
