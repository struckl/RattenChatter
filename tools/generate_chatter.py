"""Generate the Ratten Chatter voice assets.

Two stages per line of dialogue:

1. Neural text-to-speech via `edge-tts` (Microsoft Edge's online voices — free,
   no API key). Each speaker has a fixed voice plus a rate/pitch offset, and
   every individual line gets a small extra jitter on top so the same character
   never delivers two lines with identical timing.

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
    python tools/generate_chatter.py --list-voices   # show available voices
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
from conversations import CONVERSATIONS  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "RattenChatter" / "Assets" / "chatter"
SAMPLE_RATE = 24000
OUT_SAMPLE_RATE = 22050

# How each kind of transmitter sounds.
#   hp/lp      band limits in Hz
#   presence   dB bump at 2 kHz
#   ratio      compressor ratio
#   makeup     compressor makeup gain in dB
#   drive      soft-clip threshold — lower means more distortion
#   hiss       amplitude of the open-carrier noise bed
#   level      final voice level
RADIO_PROFILES = {
    "near": dict(hp=300, lp=3300, presence=4.0, ratio=5, makeup=4, drive=0.72, hiss=0.030, level=1.00),
    "far": dict(hp=430, lp=2500, presence=6.5, ratio=9, makeup=7, drive=0.52, hiss=0.080, level=0.82),
    "ground": dict(hp=420, lp=2900, presence=7.0, ratio=8, makeup=6, drive=0.58, hiss=0.055, level=0.90),
    "ground_far": dict(hp=520, lp=2300, presence=7.5, ratio=10, makeup=8, drive=0.46, hiss=0.100, level=0.78),
    "station": dict(hp=280, lp=3400, presence=3.0, ratio=4, makeup=3, drive=0.82, hiss=0.020, level=1.05),
    "cockpit_hot": dict(hp=320, lp=3100, presence=5.0, ratio=3, makeup=6, drive=0.40, hiss=0.038, level=1.10),
}


def check_tools() -> None:
    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found on PATH. Install it and try again.")


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

    click_seed = rng.randrange(1, 2**31)
    tail_seed = rng.randrange(1, 2**31)
    hiss_seed = rng.randrange(1, 2**31)

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
        f"[click][voice][tail]concat=n=3:v=0:a=1[body];"
        # Open-carrier hiss under the whole transmission.
        f"anoisesrc=c=white:r={SAMPLE_RATE}:a=1:d=30:s={hiss_seed},"
        f"highpass=f=400,lowpass=f=2600,volume={profile['hiss']}[hiss];"
        # Drive everything into a limiter set well below full scale. A real
        # receiver's AGC pins every transmission to roughly the same loudness
        # regardless of how far away the sender is, so the level differences
        # between profiles show up as tone and noise, not as volume.
        f"[body][hiss]amix=inputs=2:duration=first:normalize=0,"
        f"volume=5dB,alimiter=limit=0.55:level=disabled,"
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


async def build(only: str | None) -> None:
    check_tools()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    selected = [
        (index, conv)
        for index, conv in enumerate(CONVERSATIONS, start=1)
        if only is None or only.lower() in conv["tag"].lower()
    ]
    if not selected:
        sys.exit(f"No conversations match '{only}'.")

    if only is None:
        # Full rebuild: clear out the previous set so renumbering never leaves
        # orphaned files behind that the plugin would still load.
        for stale in OUT_DIR.glob("*.mp3"):
            stale.unlink()

    unknown = {
        speaker
        for _, conv in selected
        for speaker, _, _ in conv["lines"]
        if speaker not in CAST
    }
    if unknown:
        sys.exit(f"Unknown speakers in conversations.py: {', '.join(sorted(unknown))}")

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
                raw = tmpdir / f"raw_{conv_id}{suffix}.mp3"

                await synthesize(text, speaker, rng, raw)
                radio_filter(raw, OUT_DIR / name, speaker.profile, rng)

                manifest_rows.append(f"chatter{conv_id}|{name}|{gap:.2f}")
                done += 1
                print(f"[{done:3d}/{total_lines}] {name}  {speaker_name}: {text[:58]}")

    if only is None:
        manifest = OUT_DIR / "manifest.txt"
        manifest.write_text(
            "# Ratten Chatter conversation manifest.\n"
            "# Generated by tools/generate_chatter.py -- do not edit by hand.\n"
            "# conversation | file | seconds of dead air before this line\n"
            + "\n".join(manifest_rows)
            + "\n",
            encoding="utf-8",
        )
        print(f"\nWrote {len(manifest_rows)} clips and manifest.txt to {OUT_DIR}")
    else:
        print(f"\nWrote {len(manifest_rows)} clips (manifest left alone; rerun without --only to refresh it)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="only rebuild conversations whose tag contains this")
    parser.add_argument("--list-voices", action="store_true", help="list available English voices")
    args = parser.parse_args()

    if args.list_voices:
        asyncio.run(list_voices())
        return
    asyncio.run(build(args.only))


if __name__ == "__main__":
    main()
