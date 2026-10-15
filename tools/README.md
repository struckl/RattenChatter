# Chatter generation

The voice assets in `RattenChatter/Assets/chatter` are generated, not recorded.
Everything needed to rebuild or extend them lives here.

| File | What it is |
| --- | --- |
| `conversations.py` | The scripts. Edit this to add or change dialogue. |
| `cast.py` | Which person each callsign is (a VCTK speaker, plus an edge-tts fallback voice), and how their radio sounds. |
| `generate_chatter.py` | Text-to-speech plus the ffmpeg radio treatment. |
| `chatterbox_engine.py` | Chatterbox voice cloning on the GPU, with the checks that throw away bad takes. |
| `vctk_refs.py` | Cuts each speaker's ~12 s reference clip out of the VCTK corpus (into `refs/`, not committed). |
| `vctk/` | The VCTK speaker list and an index into the corpus mirror. |
| `preview.py` | Stitches clips into one MP3 so you can listen without the game. |

## Setup

Needs Python 3.10+ and [ffmpeg](https://ffmpeg.org/) on `PATH`. There are two
text-to-speech engines:

**Chatterbox** (the default, and what ships) —
[Chatterbox](https://github.com/resemble-ai/chatterbox) by Resemble AI (MIT)
runs locally on an NVIDIA GPU and clones every callsign from a real speaker of
the [CSTR VCTK Corpus](https://doi.org/10.7488/ds/2645) (CC BY 4.0). It needs
torch with CUDA in its own environment, a few GB of it:

```bash
python -m venv .venv-chatterbox
.venv-chatterbox/Scripts/python -m pip install "torch>=2.9" "torchaudio>=2.9" --index-url https://download.pytorch.org/whl/cu128
.venv-chatterbox/Scripts/python -m pip install -r tools/requirements-chatterbox.txt
```

The first run downloads the model (~3 GB) and a small speech recogniser into
the Hugging Face cache, and the reference clips — about 20 MB of corpus per
speaker, read straight out of the parquet mirror — into `tools/refs/`. One
environment can serve several projects: Sea Power Radio's `.venv-chatterbox`
has everything this needs.

**edge-tts** (`--engine edge`) — Microsoft Edge's online neural voices: free,
no API key, no GPU, and what shipped before Chatterbox. Needs an internet
connection.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r tools/requirements.txt
```

## Rebuild the assets

```bash
.venv-chatterbox/Scripts/python tools/generate_chatter.py
```

All 229 lines take a little over half an hour on an RTX 4070 Ti Super that is
sharing the GPU with another render; less on an idle one.

That clears `Assets/chatter` and writes a fresh set plus `manifest.txt`. While
iterating on one exchange, rebuild just that one — it takes seconds instead of
minutes:

```bash
.venv-chatterbox/Scripts/python tools/generate_chatter.py --only banter-food
```

`--only` matches against the conversation's `tag` (comma-separated for
several) and deliberately leaves `manifest.txt` alone; run without it once you
are done so the pacing gets written out.

Every Chatterbox take is checked before it is kept: one that runs far longer
than its words, or that a small speech recogniser cannot match to the script,
is re-rolled with the next seed. The log shows the speaker, delivery, length
and error rate of every line, and a `~` for each re-roll.

## Listen to the result

```bash
.venv/Scripts/python tools/preview.py --count 12
```

Writes `chatter-preview.mp3` with the same gaps the plugin uses between lines.
`--conversation 07` auditions a single exchange.

## Audition a change without touching the assets

```bash
.venv-chatterbox/Scripts/python tools/generate_chatter.py --samples
```

Renders the conversations in `SAMPLE_TAGS` (`conversations.py`) — every radio
profile, every mood, both genders and Magic — into `tools/samples/chatterbox/`
and stitches them into `tools/samples/chatterbox.mp3`. The same conversations
as they ship today land next to it as `tools/samples/shipped.mp3`, with the same
clicks and noise, so an A/B differs in the voice only. `--engine edge` renders
the edge-tts version; `--samples --only tag1,tag2` auditions any other
selection, new lines included. `Assets` is never touched.

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

Every exchange is **two speakers and two or three lines, alternating**. Two
aircraft, or an aircraft and a tower, or an aircraft and mission control. A
third voice turns something you overhear into a scene, and the player stops
flying and starts listening. `generate_chatter.py` checks this before it
generates anything and refuses to build if an exchange breaks it:

```
conversations.py:
  banter-checklist: RAZOR TWO speaks twice in a row
  cas-nine-line: 3 speaker(s), want exactly 2
```

Want a longer scene? Split it into consecutive exchanges — `BusyNetChance` in
the plugin will sometimes run two back to back anyway.

New callsigns need an entry in `cast.py`: a VCTK speaker nobody else on the
net uses (the build refuses a duplicate), picked from `vctk/speaker-info.txt`
by accent and gender, plus an edge-tts voice for the fallback
(`--list-voices` prints those). VCTK has 109 speakers but only 47 men, and
every one of them is already taken here or in Sea Power Radio, so a new man
will have to share with that mod.

Add new conversations at the end of the list if you can. Conversations are
numbered by their position, so the clips of everything after an insert get new
names — harmless, the manifest is regenerated with them, but it makes the asset
diff much larger than the change.


## How the radio effect works

Per line, the delivery first:

1. With Chatterbox, the conversation's `mood` sets how much emotion goes into
   the take (`MOOD_DELIVERY` in `generate_chatter.py`): a tense exchange is
   played harder than a routine one, a line with "!" in it (or anyone on a
   `cockpit_hot` mic in a tense exchange) is close to shouting, and controllers
   stay level however bad it gets. With edge-tts, rate and pitch get a few percent of random
   jitter instead, so the same character never delivers two lines with
   identical timing.

Then the radio:

2. Band-limited to roughly 300–3400 Hz, the width of a real comms channel.
3. A presence bump near 2 kHz so speech cuts through engine noise.
4. Hard compression, the way a transmitter's automatic level control squashes
   everything to the same loudness.
5. Soft clipping for transmitter grit.
6. Rauschen, in two layers: a steady band-limited hiss bed for the open
   carrier, plus a sparser crackle layer of individual pops and ticks riding on
   top of it. The crackle is velvet noise — random impulses rather than a
   continuous wash — which is what makes static read as static instead of as a
   fan. The hiss starts a fraction of a second before the mic click, so you
   hear the channel open before anyone speaks.
7. A mic click on the way in and a squelch tail on the way out.
8. On about one line in seven, a brief signal dropout mid-word.

How aggressive steps 2–6 are depends on the speaker's `profile` in `cast.py`.
An AWACS with a real antenna (`station`) is clean; a forward air controller on
a handheld (`ground`) is tinny; someone at the edge of the map (`far`) is thin
and hissy with busier crackle. Everything is limited to the same final level,
because a receiver's AGC does that too — so distance reads as tone and noise
rather than as volume.

### Making it louder or quieter

The chatter is mixed deliberately low: it's something you overhear while
flying, not a voice in the room. Two knobs at the top of
`generate_chatter.py`:

| | |
| --- | --- |
| `OUTPUT_CEILING` | The limiter ceiling everything lands on. `0.28` is background; raise it toward `0.5` to bring the net forward. |
| `OUTPUT_GAIN_DB` | How hard it's driven into that ceiling. Higher means the quiet parts come up too, not just the peaks. |

`hiss` and `crackle` per profile control how much Rauschen sits under the
voice. Turning those up pushes a speaker further away without changing how
loud they are.

Changing any of these means regenerating. For a quick level change with no
rebuild, the plugin's `Volume` setting scales all of it at runtime.

Randomness is seeded from the conversation tag and line number — the
Chatterbox take as well as the noise — so rebuilding produces the same voices,
the same pacing and the same noise. Only what you actually edited changes.
