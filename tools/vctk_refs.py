"""Reference clips for Chatterbox, cut from the CSTR VCTK Corpus (CC BY 4.0).

Chatterbox clones a voice from a short recording of it. For every VCTK speaker
in use this reads one row group of the speaker's mic1 recordings from the
Hugging Face parquet mirror (jspaulsen/vctk, silence-trimmed VCTK 0.92) over
HTTP range requests — about 20 MB per speaker instead of the 17.6 GB corpus —
joins utterances with short pauses until the clip runs ~12 s, and normalises
its loudness so every reference drives the cloner at the same level.

Output: tools/refs/<speaker>.wav (24 kHz mono). Not committed: the generators
call ensure_refs() and build whatever is missing on first use.

vctk/index.json maps speaker -> "shard:rowgroup:mic" -> row count, so the right
row group can be read without scanning the corpus. vctk/speaker-info.txt is the
corpus's own speaker list (age, gender, accent, region).

Usage:
    python tools/vctk_refs.py                # every speaker in cast.py
    python tools/vctk_refs.py p360 p258      # just these
    python tools/vctk_refs.py --force        # rebuild
"""

from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REFS_DIR = HERE / "refs"
INDEX_FILE = HERE / "vctk" / "index.json"
SHARD = "datasets/jspaulsen/vctk/data/train-{:05d}-of-00034.parquet"
TARGET_SECONDS = 12.0
MIN_UTTERANCE = 1.5
GAP = 0.25


def ref_path(speaker: str) -> Path:
    return REFS_DIR / f"{speaker}.wav"


def known_speakers() -> set[str]:
    return set(json.loads(INDEX_FILE.read_text(encoding="utf-8")))


def _row_group(speaker: str) -> tuple[int, int]:
    """The row group holding the most mic1 recordings of this speaker."""
    entries = json.loads(INDEX_FILE.read_text(encoding="utf-8"))[speaker]
    groups = [(n, k) for k, n in entries.items() if k.endswith(":mic1")] or [(n, k) for k, n in entries.items()]
    _, key = max(groups)
    shard, rg, _ = key.split(":")
    return int(shard), int(rg)


def _utterances(fs, speaker: str):
    import numpy as np
    import pyarrow.parquet as pq
    import soundfile as sf

    shard, rg = _row_group(speaker)
    with fs.open(SHARD.format(shard), "rb", block_size=1 << 20) as f:
        table = pq.ParquetFile(f).read_row_group(rg, columns=["id", "speaker_id", "mic_id", "audio"])
    rows = [r for r in table.to_pylist() if r["speaker_id"] == speaker]
    mic1 = [r for r in rows if r["mic_id"] == "mic1"] or rows
    for r in sorted(mic1, key=lambda r: r["id"]):
        data, sr = sf.read(io.BytesIO(r["audio"]["bytes"]), dtype="float32", always_2d=False)
        yield (data.mean(axis=1) if data.ndim > 1 else data).astype(np.float32), sr


def build(fs, speaker: str) -> None:
    import numpy as np
    import soundfile as sf

    parts, total, sr = [], 0.0, None
    for data, rate in _utterances(fs, speaker):
        sr = sr or rate
        if rate != sr or len(data) / rate < MIN_UTTERANCE:
            continue
        parts += [data, np.zeros(int(GAP * sr), dtype=np.float32)]
        total += len(data) / rate + GAP
        if total >= TARGET_SECONDS:
            break
    if not parts:
        sys.exit(f"No usable VCTK recordings for {speaker}.")
    REFS_DIR.mkdir(exist_ok=True)
    raw = REFS_DIR / f"{speaker}_raw.wav"
    sf.write(str(raw), np.concatenate(parts), sr)
    # EBU R128 loudness so every reference drives the cloner at the same level.
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw),
         "-af", "loudnorm=I=-20:TP=-2:LRA=11", "-ac", "1", "-ar", "24000", str(ref_path(speaker))],
        capture_output=True, text=True,
    )
    raw.unlink()
    if result.returncode != 0:
        sys.exit(f"ffmpeg failed on {speaker}:\n{result.stderr}")
    print(f"  reference {speaker}: {total:.1f}s", flush=True)


def ensure_refs(speakers, force: bool = False) -> None:
    unknown = sorted(set(speakers) - known_speakers())
    if unknown:
        sys.exit(f"Not VCTK speakers (see tools/vctk/speaker-info.txt): {', '.join(unknown)}")
    todo = [s for s in dict.fromkeys(speakers) if force or not ref_path(s).exists()]
    if not todo:
        return
    from huggingface_hub import HfFileSystem

    fs = HfFileSystem()
    for speaker in todo:
        build(fs, speaker)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("speakers", nargs="*", help="VCTK speaker ids (default: everyone in cast.py)")
    parser.add_argument("--force", action="store_true", help="rebuild clips that already exist")
    args = parser.parse_args()
    if args.speakers:
        speakers = args.speakers
    else:
        sys.path.insert(0, str(HERE))
        from cast import CAST

        speakers = [s.vctk for s in CAST.values()]
    ensure_refs(speakers, force=args.force)


if __name__ == "__main__":
    main()
