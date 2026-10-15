"""Generate the Ratten Chatter voice assets.

Two stages per line of dialogue:

1. Text-to-speech, with one of two engines:

   chatterbox (default)  Chatterbox (Resemble AI, MIT) on the local GPU clones
       each callsign's VCTK speaker (see cast.py and chatterbox_engine.py).
       A real person's voice, timing and breath instead of a stock announcer.
       Delivery follows the conversation's mood: a tense exchange or a line
       with "!" in it gets more exaggeration, a controller stays level. Each
       line's take is seeded from its tag, so a rebuild says it the same way.

   edge  The original pipeline and the fallback for a machine without a GPU:
       Microsoft Edge's online neural voices via `edge-tts` (free, no API key).
       Each speaker has a fixed voice plus a rate/pitch offset, and every line
       gets a small extra jitter on top so the same character never delivers
       two lines with identical timing.

2. A radio treatment in ffmpeg, which is what actually sells it:
     * band-limited to roughly 300–3400 Hz, like a real comms channel
     * a presence bump around 2 kHz so it cuts through engine noise
     * heavy compression, the way an ALC-equipped transmitter squashes speech
     * soft clipping for transmitter grit
     * an open-carrier hiss bed under the whole transmission
     * a mic click on the way in and a squelch tail on the way out
     * on some lines, a short signal dropout mid-word

   Distant or handheld speakers get a narrower, hissier, more distorted
   treatment than an AWACS with a proper antenna. That contrast is most of the
   reason the net sounds like a place instead of a playlist.

Output goes to RattenChatter/Assets/chatter as chatter01a.mp3, chatter01b.mp3,
... plus a manifest.txt telling the plugin which files belong to which
conversation and how long to wait before each reply.

Everything is seeded off the conversation tag, so regenerating produces byte-
comparable pacing and noise — only the text changes when you edit a script.

Usage:
    python tools/generate_chatter.py                 # regenerate everything
    python tools/generate_chatter.py --only banter   # only tags containing "banter"
    python tools/generate_chatter.py --samples       # audition reel, Assets untouched
    python tools/generate_chatter.py --engine edge   # the edge-tts fallback
    python tools/generate_chatter.py --list-voices   # show available edge-tts voices
"""

from __future__ import annotations

import argparse
import asyncio
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import edge_tts

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cast import CAST  # noqa: E402
from conversations import CONVERSATIONS, SAMPLE_TAGS  # noqa: E402
import preview  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "RattenChatter" / "Assets" / "chatter"
SAMPLES_DIR = Path(__file__).resolve().parent / "samples"
SAMPLE_RATE = 24000
OUT_SAMPLE_RATE = 22050

# How loud the finished transmissions sit. This is deliberately well below full
# scale: the chatter is background, something you overhear while flying, not a
# voice in the room. Raise OUTPUT_CEILING if you want it further forward.
OUTPUT_GAIN_DB = 2
OUTPUT_CEILING = 0.28

# How each kind of transmitter sounds.
#   hp/lp      band limits in Hz
#   presence   dB bump at 2 kHz
#   ratio      compressor ratio
#   makeup     compressor makeup gain in dB
#   drive      soft-clip threshold — lower means more distortion
#   hiss       amplitude of the steady open-carrier hiss under the voice
#   crackle    amplitude of the sparse crackle/static layer on top of the hiss
#   level      final voice level
RADIO_PROFILES = {
    "near": dict(hp=300, lp=3300, presence=4.0, ratio=5, makeup=4, drive=0.72, hiss=0.075, crackle=0.10, level=0.92),
    "far": dict(hp=430, lp=2500, presence=6.5, ratio=9, makeup=7, drive=0.52, hiss=0.170, crackle=0.24, level=0.74),
    "ground": dict(hp=420, lp=2900, presence=7.0, ratio=8, makeup=6, drive=0.58, hiss=0.120, crackle=0.18, level=0.84),
    "ground_far": dict(hp=520, lp=2300, presence=7.5, ratio=10, makeup=8, drive=0.46, hiss=0.200, crackle=0.28, level=0.70),
    "station": dict(hp=280, lp=3400, presence=3.0, ratio=4, makeup=3, drive=0.82, hiss=0.055, crackle=0.07, level=1.00),
    "cockpit_hot": dict(hp=320, lp=3100, presence=5.0, ratio=3, makeup=6, drive=0.40, hiss=0.090, crackle=0.12, level=1.00),
}


# Chatterbox delivery per conversation mood: (exaggeration, cfg_weight).
# exaggeration is how much emotion goes in; cfg_weight is how tightly the take
# follows the reference speaker's pacing — lower is steadier, which offsets the
# rush high exaggeration brings. Same scale Sea Power Radio uses for its
# urgency levels.
MOOD_DELIVERY = {
    "routine": (0.50, 0.50),
    "background": (0.50, 0.50),
    "banter": (0.55, 0.50),
    "grim": (0.45, 0.50),
    "tense": (0.65, 0.40),
}
URGENT_DELIVERY = (0.85, 0.30)


def delivery(mood: str, speaker, text: str) -> tuple[float, float]:
    """How hard a line is played: the mood, then the person, then the words."""
    exaggeration, cfg_weight = MOOD_DELIVERY[mood]
    if speaker.profile == "station":
        # Controllers are trained to sound bored however bad it gets. That
        # contrast with the aircrew is half of what makes a tense net tense.
        exaggeration, cfg_weight = min(exaggeration, 0.55), max(cfg_weight, 0.45)
    if "!" in text or (speaker.profile == "cockpit_hot" and mood == "tense"):
        exaggeration, cfg_weight = URGENT_DELIVERY
    return exaggeration, cfg_weight


def check_tools() -> None:
    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found on PATH. Install it and try again.")


def validate(conversations) -> None:
    """Enforce the shape rules from the top of conversations.py.

    These are easy to break by accident while editing and impossible to notice
    afterwards without listening to all of it, so fail the build instead.
    """
    problems: list[str] = []
    for conv in conversations:
        tag = conv["tag"]
        speakers = [name for name, _, _ in conv["lines"]]

        unknown = [name for name in speakers if name not in CAST]
        if unknown:
            problems.append(f"{tag}: unknown speaker(s) {', '.join(sorted(set(unknown)))}")
        if not 2 <= len(speakers) <= 3:
            problems.append(f"{tag}: {len(speakers)} lines, want 2 or 3")
        distinct = len(set(speakers))
        if distinct != 2:
            problems.append(f"{tag}: {distinct} speaker(s), want exactly 2")
        for previous, current in zip(speakers, speakers[1:]):
            if previous == current:
                problems.append(f"{tag}: {current} speaks twice in a row")
        if conv["mood"] not in MOOD_DELIVERY:
            problems.append(f"{tag}: unknown mood '{conv['mood']}'")

    tags = {conv["tag"] for conv in conversations}
    problems += [f"SAMPLE_TAGS: unknown tag '{tag}'" for tag in SAMPLE_TAGS if tag not in tags]
    by_vctk: dict[str, list[str]] = {}
    for name, speaker in CAST.items():
        by_vctk.setdefault(speaker.vctk, []).append(name)
    problems += [f"cast.py: {', '.join(names)} share VCTK speaker '{vctk or '(none)'}'"
                 for vctk, names in by_vctk.items() if len(names) > 1 or not vctk]

    if problems:
        sys.exit("conversations.py:\n  " + "\n  ".join(problems))


async def list_voices() -> None:
    for voice in await edge_tts.list_voices():
        if voice["Locale"].startswith("en-"):
            print(f"{voice['ShortName']:42} {voice['Gender']}")


def jitter_prosody(speaker, rng: random.Random) -> tuple[str, str]:
    """Nudge the speaker's rate and pitch a little for this one line.

    Humans do not deliver every transmission at exactly the same tempo. TTS
    does, and that is the single biggest tell. A few percent of wobble per line
    costs nothing and removes most of it.
    """
    base_rate = int(speaker.rate.rstrip("%"))
    base_pitch = int(speaker.pitch.rstrip("Hz"))
    rate = base_rate + rng.randint(-4, 4)
    pitch = base_pitch + rng.randint(-3, 3)
    return f"{rate:+d}%", f"{pitch:+d}Hz"


async def synthesize(text: str, speaker, rng: random.Random, dest: Path) -> None:
    rate, pitch = jitter_prosody(speaker, rng)
    communicate = edge_tts.Communicate(
        text,
        voice=speaker.voice,
        rate=rate,
        pitch=pitch,
    )
    await communicate.save(str(dest))


def build_filtergraph(profile: dict, rng: random.Random, dropout: bool) -> str:
    """Assemble the ffmpeg filtergraph for one transmission."""
    click_dur = round(rng.uniform(0.022, 0.048), 3)
    click_level = round(rng.uniform(0.16, 0.30), 3)
    tail_dur = round(rng.uniform(0.09, 0.20), 3)
    tail_level = round(rng.uniform(0.20, 0.36), 3)
    # A beat of open carrier after the last word, before the squelch closes.
    hang = round(rng.uniform(0.05, 0.16), 3)

    voice_chain = [
        "aformat=sample_fmts=fltp:channel_layouts=mono",
        f"aresample={SAMPLE_RATE}",
        # Trim the TTS engine's leading and trailing silence so the mic click
        # lands right before the first word and the squelch closes right after
        # the last one. Trailing silence is done by reversing, trimming the
        # (now leading) silence and reversing back: silenceremove's own stop_*
        # mode truncates at the first internal pause instead.
        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.01",
        "areverse",
        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02",
        "areverse",
        f"highpass=f={profile['hp']}",
        f"lowpass=f={profile['lp']}",
        f"equalizer=f=2000:t=q:w=1.3:g={profile['presence']}",
        f"acompressor=threshold=-20dB:ratio={profile['ratio']}"
        f":attack=4:release=90:makeup={profile['makeup']}",
        f"asoftclip=type=atan:threshold={profile['drive']}:oversample=4",
        # Re-limit the band after distortion, which always adds harmonics above it.
        f"highpass=f={profile['hp']}",
        f"lowpass=f={profile['lp']}",
    ]
    if dropout:
        start = round(rng.uniform(0.35, 1.1), 2)
        length = round(rng.uniform(0.05, 0.13), 3)
        voice_chain.append(
            f"volume=volume=0.08:enable='between(t,{start},{round(start + length, 3)})'"
        )
    voice_chain.append(f"volume={profile['level']}")
    voice_chain.append(f"apad=pad_dur={hang}")

    # A moment of open carrier before the mic click, so you hear the channel
    # open before anyone speaks rather than the noise appearing with the voice.
    preroll_ms = rng.randint(90, 220)

    click_seed = rng.randrange(1, 2**31)
    tail_seed = rng.randrange(1, 2**31)
    hiss_seed = rng.randrange(1, 2**31)
    crackle_seed = rng.randrange(1, 2**31)
    # Sparser crackle on a strong signal, busier on a weak one.
    density = round(rng.uniform(0.02, 0.05) * (1.6 if profile["hiss"] > 0.1 else 1.0), 4)

    return (
        f"[0:a]{','.join(voice_chain)}[voice];"
        # Mic click: a very short, hard-decaying noise burst.
        f"anoisesrc=c=white:r={SAMPLE_RATE}:a=1:d={click_dur}:s={click_seed},"
        f"highpass=f=700,lowpass=f=3200,"
        f"afade=t=out:st=0:d={click_dur}:curve=exp,volume={click_level}[click];"
        # Squelch tail: longer, brighter, the noise burst you get when the
        # carrier drops and the receiver opens up for a moment.
        f"anoisesrc=c=white:r={SAMPLE_RATE}:a=1:d={tail_dur}:s={tail_seed},"
        f"highpass=f=500,lowpass=f=3400,"
        f"afade=t=out:st=0.015:d={round(tail_dur - 0.015, 3)}:curve=log,"
        f"volume={tail_level}[tail];"
        f"[click][voice][tail]concat=n=3:v=0:a=1,adelay={preroll_ms}:all=1[body];"
        # Steady open-carrier hiss under the whole transmission.
        f"anoisesrc=c=white:r={SAMPLE_RATE}:a=1:d=30:s={hiss_seed},"
        f"highpass=f=400,lowpass=f=2600,volume={profile['hiss']}[hiss];"
        # Crackle on top of it. Velvet noise is sparse impulses rather than a
        # continuous wash, which is what makes static sound like static instead
        # of like a fan: individual pops and ticks riding the hiss.
        f"anoisesrc=c=velvet:density={density}:r={SAMPLE_RATE}:a=1:d=30:s={crackle_seed},"
        f"highpass=f=600,lowpass=f=3200,volume={profile['crackle']}[crackle];"
        # Drive everything into a limiter set well below full scale. A real
        # receiver's AGC pins every transmission to roughly the same loudness
        # regardless of how far away the sender is, so the level differences
        # between profiles show up as tone and noise, not as volume.
        f"[body][hiss][crackle]amix=inputs=3:duration=first:normalize=0,"
        f"volume={OUTPUT_GAIN_DB}dB,alimiter=limit={OUTPUT_CEILING}:level=disabled,"
        f"aresample={OUT_SAMPLE_RATE}[out]"
    )


def radio_filter(src: Path, dest: Path, profile_name: str, rng: random.Random) -> None:
    profile = RADIO_PROFILES[profile_name]
    # Roughly one line in seven takes a hit. More than that reads as broken.
    dropout = rng.random() < 0.14
    graph = build_filtergraph(profile, rng, dropout)
    result = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(src),
            "-filter_complex", graph,
            "-map", "[out]",
            "-c:a", "libmp3lame", "-q:a", "5",
            "-ar", str(OUT_SAMPLE_RATE), "-ac", "1",
            str(dest),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit(f"ffmpeg failed on {src.name}:\n{result.stderr}")


def write_manifest(out_dir: Path, rows: list[str]) -> None:
    (out_dir / "manifest.txt").write_text(
        "# Ratten Chatter conversation manifest.\n"
        "# Generated by tools/generate_chatter.py -- do not edit by hand.\n"
        "# conversation | file | seconds of dead air before this line\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )


async def build(only: str | None, engine_name: str, samples: bool) -> None:
    check_tools()
    # Always validate the whole file, not just the selection, so a broken
    # exchange cannot hide behind an --only run.
    validate(CONVERSATIONS)

    numbered = list(enumerate(CONVERSATIONS, start=1))
    wanted = [part.strip().lower() for part in only.split(",")] if only else []
    matching = [(index, conv) for index, conv in numbered
                if any(part in conv["tag"].lower() for part in wanted)]
    if samples:
        # Same file names as the real set, so a sample clip and the shipped
        # clip it would replace can be compared directly. --only swaps the
        # standard audition set for a selection of its own, e.g. new lines.
        reel_name = engine_name if only is None else f"{engine_name}-only"
        out_dir = SAMPLES_DIR / reel_name
        if only is None:
            selected = [(index, conv) for index, conv in numbered if conv["tag"] in SAMPLE_TAGS]
        else:
            selected = matching
        shutil.rmtree(out_dir, ignore_errors=True)
    else:
        out_dir = OUT_DIR
        selected = numbered if only is None else matching
    if not selected:
        sys.exit(f"No conversations match '{only}'.")
    out_dir.mkdir(parents=True, exist_ok=True)

    if only is None and not samples:
        # Full rebuild: clear out the previous set so renumbering never leaves
        # orphaned files behind that the plugin would still load. The manifest
        # goes too — if this run dies partway through, a leftover manifest
        # pointing at deleted clips is worse than none at all, and its absence
        # is how we can tell the build did not finish.
        for stale in out_dir.glob("*.mp3"):
            stale.unlink()
        (out_dir / "manifest.txt").unlink(missing_ok=True)

    engine = None
    if engine_name == "chatterbox":
        from chatterbox_engine import ChatterboxEngine

        engine = ChatterboxEngine()

    manifest_rows: list[str] = []
    total_lines = sum(len(conv["lines"]) for _, conv in selected)
    done = 0

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for index, conv in selected:
            conv_id = f"{index:02d}"
            for line_index, (speaker_name, text, gap) in enumerate(conv["lines"]):
                speaker = CAST[speaker_name]
                # Deterministic per line: same script means same pacing and noise.
                rng = random.Random(f"{conv['tag']}|{line_index}|{speaker_name}")
                suffix = chr(ord("a") + line_index)
                name = f"chatter{conv_id}{suffix}.mp3"

                if engine is None:
                    raw = tmpdir / f"raw_{conv_id}{suffix}.mp3"
                    await synthesize(text, speaker, rng, raw)
                    note = ""
                else:
                    raw = tmpdir / f"raw_{conv_id}{suffix}.wav"
                    # Draw the jitter edge-tts would have used anyway, so both
                    # engines get the same clicks, hiss and dropouts and an A/B
                    # between them differs in the voice only.
                    jitter_prosody(speaker, rng)
                    exaggeration, cfg_weight = delivery(conv["mood"], speaker, text)
                    take = engine.say(speaker.vctk, text, raw, seed=f"{conv['tag']}|{line_index}",
                                      exaggeration=exaggeration, cfg_weight=cfg_weight)
                    retries = "" if take.tries == 1 else f" x{take.tries}"
                    note = (f"  [{speaker.vctk} ex {exaggeration:.2f} cfg {cfg_weight:.2f} "
                            f"{take.seconds:.1f}s CER {take.cer:.2f}{retries}]")
                radio_filter(raw, out_dir / name, speaker.profile, rng)

                manifest_rows.append(f"chatter{conv_id}|{name}|{gap:.2f}")
                done += 1
                print(f"[{done:3d}/{total_lines}] {name}  {speaker_name}: {text[:58]}{note}", flush=True)

    if samples:
        write_manifest(out_dir, manifest_rows)
        if only is None:
            keys = [f"chatter{index:02d}" for tag in SAMPLE_TAGS
                    for index, conv in numbered if conv["tag"] == tag]
        else:
            keys = [f"chatter{index:02d}" for index, _ in selected]
        reel = SAMPLES_DIR / f"{reel_name}.mp3"
        seconds = preview.stitch(out_dir, keys, reel)
        print(f"\nReel: {reel} ({seconds:.0f} s, {len(keys)} conversations)")
        if only is None and (OUT_DIR / "manifest.txt").exists():
            # The same conversations as they ship today, for an A/B.
            shipped = SAMPLES_DIR / "shipped.mp3"
            preview.stitch(OUT_DIR, keys, shipped)
            print(f"Shipped set, same conversations: {shipped}")
    elif only is None:
        write_manifest(out_dir, manifest_rows)
        print(f"\nWrote {len(manifest_rows)} clips and manifest.txt to {out_dir}")
    else:
        print(f"\nWrote {len(manifest_rows)} clips (manifest left alone; rerun without --only to refresh it)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", help="only rebuild conversations whose tag contains this "
                                       "(comma-separated for several)")
    parser.add_argument("--engine", choices=("chatterbox", "edge"), default="chatterbox",
                        help="text-to-speech engine (default: chatterbox)")
    parser.add_argument("--samples", action="store_true",
                        help="render SAMPLE_TAGS (or the --only selection) into tools/samples plus a reel; "
                             "Assets untouched")
    parser.add_argument("--list-voices", action="store_true", help="list available edge-tts voices")
    args = parser.parse_args()

    if args.list_voices:
        asyncio.run(list_voices())
        return
    asyncio.run(build(args.only, args.engine, args.samples))


if __name__ == "__main__":
    main()
