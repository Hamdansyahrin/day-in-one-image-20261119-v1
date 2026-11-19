# day-in-one-image-20261119-v1

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Hamdansyahrin/day-in-one-image-20261119-v1/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Hamdansyahrin/day-in-one-image-20261119-v1/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

One Day, One Page: the world news of **Thursday, 19 November 2026** drawn as a
single broadsheet front page — 45 stories on one 1024×1024 image. The three
leads are the first Trump–Xi–Putin three-way summit in Shenzhen, Ukraine's
third strike on the Crimean Bridge in a week, and Iran's strikes on Gulf
states after the US attack on Qeshm island. Ten more illustrated cards cover
Anthropic's record $83 IPO, the world court's coming Myanmar genocide ruling,
GTA VI's launch, Voyager 1 reaching one light-day from Earth, Cyclone Akvan,
the EU's proposed €45bn Ukraine loan, the COP31 deadlock, Ebola vaccine
trials in DR Congo, California's record atmospheric river and Israel's push
beyond the Yellow Line in Gaza. A markets strip, a pinned world map keyed to
the 13 illustrated stories and a 32-item index of the day's other stories
complete the page. Every picture is drawn by program with Pillow — no
photographs — and all text is set in Liberation Serif and Sans, so nothing
on the page is garbled.

`main.py` is the graded entrypoint (Python 3.13, standard library only): it
validates `entry.png` — PNG signature, a full chunk walk to IEND with no
trailing bytes, the 1 MiB and 1024 px caps — copies it to the output
directory and verifies the copy by SHA-256 read-back. `render.py` is the
deterministic renderer that produced `entry.png`; run it again and the
bytes are identical.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=748tdgv2&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
