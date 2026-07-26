# Chatter generation

The voice assets in `RattenChatter/Assets/chatter` are generated, not recorded.
Everything needed to rebuild or extend them lives here.

| File | What it is |
| --- | --- |
| `conversations.py` | The scripts. Edit this to add or change dialogue. |
| `cast.py` | Which neural voice each callsign uses, and how their radio sounds. |
| `generate_chatter.py` | Text-to-speech plus the ffmpeg radio treatment. |
| `preview.py` | Stitches clips into one MP3 so you can listen without the game. |

## Setup

Needs Python 3.9+, [ffmpeg](https://ffmpeg.org/) on `PATH`, and an internet
connection (the TTS voices are Microsoft Edge's online neural voices — free, no
API key, no account).

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r tools/requirements.txt
```

## Rebuild the assets

```bash
.venv/Scripts/python tools/generate_chatter.py
```

That clears `Assets/chatter` and writes a fresh set plus `manifest.txt`. While
iterating on one exchange, rebuild just that one — it takes seconds instead of
minutes:

```bash
.venv/Scripts/python tools/generate_chatter.py --only banter-food
```

`--only` matches against the conversation's `tag` and deliberately leaves
`manifest.txt` alone; run without it once you are done so the pacing gets
written out.

## Listen to the result

```bash
.venv/Scripts/python tools/preview.py --count 12
```

Writes `chatter-preview.mp3` with the same gaps the plugin uses between lines.
`--conversation 07` auditions a single exchange.

## Adding dialogue

Append a dict to `CONVERSATIONS` in `conversations.py`:

```python
dict(
    tag="banter-checklist",
    mood="banter",
    lines=[
        ("RAZOR ONE", "Razor two, did you actually do the fuel check?", 0),
        ("RAZOR TWO", "Define check.", 1.1),
    ],
),
```

The third element of each line is the dead air before it, in seconds — `0.4` is
a snap answer, `1.2` is normal, `3.0` is someone actually looking something up.
Write numbers as words ("two seven zero", "flight level two four zero") or the
TTS reads them like a calculator.

New callsigns need an entry in `cast.py`. `python tools/generate_chatter.py
--list-voices` prints everything available; there are around forty English
voices across a dozen accents, so there is no need to reuse one.

Conversations are numbered by their position in the list, so inserting one in
the middle renumbers the files after it. That is fine — the manifest is
regenerated with them.

## How the radio effect works

Per line, after TTS:

1. Rate and pitch get a few percent of random jitter, so the same character
   never delivers two lines with identical timing. This is the single biggest
   thing separating "person on a radio" from "screen reader".
2. Band-limited to roughly 300–3400 Hz, the width of a real comms channel.
3. A presence bump near 2 kHz so speech cuts through engine noise.
4. Hard compression, the way a transmitter's automatic level control squashes
   everything to the same loudness.
5. Soft clipping for transmitter grit.
6. An open-carrier hiss bed, a mic click on the way in, a squelch tail on the
   way out.
7. On about one line in seven, a brief signal dropout mid-word.

How aggressive steps 2–6 are depends on the speaker's `profile` in `cast.py`.
An AWACS with a real antenna (`station`) is clean and loud; a forward air
controller on a handheld (`ground`) is tinny; someone at the edge of the map
(`far`) is thin and hissy. Everything is limited to the same final level,
because a receiver's AGC does that too — so distance reads as tone and noise
rather than as volume.

Randomness is seeded from the conversation tag and line number, so rebuilding
produces the same pacing and the same noise. Only what you actually edited
changes.
