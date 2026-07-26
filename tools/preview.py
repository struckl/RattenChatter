"""Stitch generated chatter into one MP3 so you can audition it without the game.

Reads Assets/chatter/manifest.txt and lays the clips out on a timeline using the
same pacing the plugin uses: each line's recorded gap before it, and a pause
between conversations.

Usage:
    python tools/preview.py                      # 8 random conversations
    python tools/preview.py --count 20
    python tools/preview.py --conversation 05    # just one, by number
    python tools/preview.py --out demo.mp3
"""

from __future__ import annotations

import argparse
import random
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHATTER_DIR = REPO / "RattenChatter" / "Assets" / "chatter"
CONVERSATION_PAUSE = 3.0


def read_manifest() -> dict[str, list[tuple[str, float]]]:
    manifest = CHATTER_DIR / "manifest.txt"
    if not manifest.exists():
        sys.exit(f"No manifest at {manifest}. Run tools/generate_chatter.py first.")

    conversations: dict[str, list[tuple[str, float]]] = {}
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        row = raw.strip()
        if not row or row.startswith("#"):
            continue
        conv_id, name, gap = row.split("|")
        conversations.setdefault(conv_id, []).append((name, float(gap)))
    return conversations


def clip_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=8, help="how many conversations to include")
    parser.add_argument("--conversation", help="only this conversation, e.g. 05")
    parser.add_argument("--out", default="chatter-preview.mp3", help="output file")
    parser.add_argument("--seed", type=int, default=0, help="which random selection to use")
    args = parser.parse_args()

    conversations = read_manifest()
    if args.conversation:
        key = f"chatter{args.conversation.zfill(2)}"
        if key not in conversations:
            sys.exit(f"No conversation '{key}'. Have {len(conversations)}.")
        chosen = [key]
    else:
        keys = sorted(conversations)
        rng = random.Random(args.seed)
        chosen = rng.sample(keys, min(args.count, len(keys)))

    # Lay every clip out on one silent bed with adelay, then mix. Simpler and
    # more accurate than concatenating silence segments.
    inputs: list[str] = []
    parts: list[str] = []
    cursor = 0.0
    for conv_index, key in enumerate(chosen):
        if conv_index:
            cursor += CONVERSATION_PAUSE
        for line_index, (name, gap) in enumerate(conversations[key]):
            path = CHATTER_DIR / name
            if line_index:
                cursor += gap
            inputs += ["-i", str(path)]
            index = len(inputs) // 2 - 1
            parts.append(f"[{index}:a]adelay={int(cursor * 1000)}:all=1[d{index}]")
            cursor += clip_duration(path)

    mix = "".join(f"[d{i}]" for i in range(len(parts)))
    graph = ";".join(parts) + f";{mix}amix=inputs={len(parts)}:normalize=0:dropout_transition=0[out]"

    out = Path(args.out)
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs,
         "-filter_complex", graph, "-map", "[out]",
         "-c:a", "libmp3lame", "-q:a", "4", "-ar", "22050", "-ac", "1", str(out)],
        check=True,
    )
    print(f"Wrote {out} — {len(chosen)} conversations, {cursor:.0f} seconds:")
    for key in chosen:
        print(f"  {key}  ({len(conversations[key])} transmissions)")


if __name__ == "__main__":
    main()
