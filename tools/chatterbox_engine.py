"""Local voice cloning with Chatterbox (Resemble AI, MIT licence) on the GPU.

edge-tts reads text in a stock neural voice. Chatterbox instead clones a real
person from a ~12 second recording of them, and it is the difference between a
competent announcer and somebody actually keying a mic. The people it clones
are speakers from the CSTR VCTK Corpus (CC BY 4.0) — studio recordings made for
exactly this kind of research, with a clean licence for redistributing what
comes out. `vctk_refs.py` builds the reference clips.

Sampling is random, so every take is seeded from a caller-supplied key: the
same text for the same speaker comes out the same on every rebuild. Sampling
also occasionally goes wrong — a swallowed word, a stutter, a few seconds of
breathing after the last word. Every take is therefore checked twice before it
is kept:

  * length: anything longer than ~0.9 s per word (+1 s) is a hallucination;
  * content: a small speech recogniser (wav2vec2, CTC, greedy) transcribes the
    take, and the character error rate against the script has to stay under
    MAX_CER. Callsigns and brevity words are not in its vocabulary, so this is
    a coarse net for garbage, not a spell checker.

A take that fails is re-rolled with the next seed, up to MAX_TRIES; if none
passes, the best one is kept and reported, so a full build never stops on one
stubborn line.

Short lines are where Chatterbox is weakest: a one-word take often comes with a
breath or a stray syllable in front of the word, and the delivery varies a lot
from seed to seed. Two options for callers where that matters:

  * trim: the same recogniser force-aligns the script against the take (CTC
    Viterbi, as in Sea Power Radio's align.py) and the take is cut to the
    spoken words plus a few milliseconds, so nothing comes before the word;
  * context: render the line with a few words in front of it ("Notch!
    Notch!") and cut those away again — the model is far steadier with
    something to lead into;
  * candidates: collect several passing takes and keep the tightest one.

Every Chatterbox output carries Resemble AI's inaudible Perth watermark.

Needs torch with CUDA, chatterbox-tts, soundfile and transformers — see
requirements-chatterbox.txt. The first run downloads the model (~3 GB) and the
recogniser (~360 MB) into the Hugging Face cache.
"""

from __future__ import annotations

import re
import zlib
from dataclasses import dataclass
from pathlib import Path

import soundfile as sf
import torch
import torchaudio

from vctk_refs import ensure_refs, ref_path

ASR_MODEL = "facebook/wav2vec2-base-960h"
ASR_SAMPLE_RATE = 16000

MAX_TRIES = 4
SECONDS_PER_WORD_MAX = 0.9
MAX_CER = 0.4

# How much of the take survives either side of the aligned words when trimming.
# CTC tends to mark a word from its vowel and to end it before a trailing
# fricative fades, so both sides keep a little more than the alignment says.
TRIM_LEAD = 0.06
TRIM_TAIL = 0.12


def normalize_words(text: str) -> list[str]:
    """Upper-case letters and apostrophes only, the alphabet the recogniser writes in."""
    text = text.upper().replace("-", " ")
    return [w for w in (re.sub(r"[^A-Z']", "", t) for t in text.split()) if w]


def char_error_rate(reference: str, hypothesis: str) -> float:
    previous = list(range(len(hypothesis) + 1))
    for i, r in enumerate(reference, start=1):
        current = [i]
        for j, h in enumerate(hypothesis, start=1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (r != h)))
        previous = current
    return previous[-1] / max(1, len(reference))


class SpeechCheck:
    """wav2vec2 CTC: greedy transcription to tell speech from garbage, and forced
    alignment to find where the words are."""

    def __init__(self, device: str) -> None:
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
        from transformers.utils import logging

        # The CTC head's unused pretraining weights are not worth a warning, and
        # a progress bar per load buries the generator's own output.
        logging.set_verbosity_error()
        logging.disable_progress_bar()
        self.device = device
        self.processor = Wav2Vec2Processor.from_pretrained(ASR_MODEL)
        self.model = Wav2Vec2ForCTC.from_pretrained(ASR_MODEL).to(device).eval()
        self.vocab = self.processor.tokenizer.get_vocab()
        self.blank = self.vocab[self.processor.tokenizer.pad_token]

    def _emission(self, wav: torch.Tensor, sr: int) -> tuple[torch.Tensor, float]:
        """Log-probabilities per frame, and the seconds each frame covers."""
        audio = torchaudio.functional.resample(wav, sr, ASR_SAMPLE_RATE)
        inputs = self.processor(audio.numpy(), sampling_rate=ASR_SAMPLE_RATE, return_tensors="pt")
        with torch.inference_mode():
            logits = self.model(inputs.input_values.to(self.device)).logits[0]
        emission = torch.log_softmax(logits, dim=-1).cpu()
        return emission, audio.size(0) / emission.size(0) / ASR_SAMPLE_RATE

    def cer(self, wav: torch.Tensor, sr: int, text: str) -> tuple[float, str]:
        emission, _ = self._emission(wav, sr)
        heard = self.processor.batch_decode(emission.argmax(dim=-1).unsqueeze(0))[0]
        heard = " ".join(heard.split())
        return char_error_rate(" ".join(normalize_words(text)), heard), heard

    def word_spans(self, wav: torch.Tensor, sr: int, text: str) -> list[tuple[float, float]]:
        """(start, end) in seconds of every word of the script (forced alignment)."""
        emission, seconds_per_frame = self._emission(wav, sr)
        words = normalize_words(text)
        tokens = [self.vocab[c] for c in "|" + "|".join(words) + "|"]
        frames: dict[int, list[int]] = {}
        for token, frame in self._backtrack(self._trellis(emission, tokens), emission, tokens):
            frames.setdefault(token, []).append(frame)
        spans = []
        first = 1  # token 0 is the leading separator
        for word in words:
            last = first + len(word) - 1
            spans.append((min(frames[first]) * seconds_per_frame, (max(frames[last]) + 1) * seconds_per_frame))
            first = last + 2  # skip the separator
        return spans

    def _trellis(self, emission: torch.Tensor, tokens: list[int]) -> torch.Tensor:
        num_frames, num_tokens = emission.size(0), len(tokens)
        trellis = torch.zeros((num_frames, num_tokens))
        trellis[1:, 0] = torch.cumsum(emission[1:, self.blank], 0)
        trellis[0, 1:] = -float("inf")
        trellis[-num_tokens + 1:, 0] = float("inf")
        tok = torch.tensor(tokens)
        for t in range(num_frames - 1):
            trellis[t + 1, 1:] = torch.maximum(
                trellis[t, 1:] + emission[t, self.blank],
                trellis[t, :-1] + emission[t, tok[1:]],
            )
        return trellis

    def _backtrack(self, trellis: torch.Tensor, emission: torch.Tensor,
                   tokens: list[int]) -> list[tuple[int, int]]:
        t, j = trellis.size(0) - 1, trellis.size(1) - 1
        path = [(j, t)]
        while j > 0:
            if t <= 0:
                raise ValueError("alignment failed (audio shorter than transcript)")
            stayed = trellis[t - 1, j] + emission[t - 1, self.blank]
            changed = trellis[t - 1, j - 1] + emission[t - 1, tokens[j]]
            t -= 1
            if changed > stayed:
                j -= 1
            path.append((j, t))
        return path[::-1]


@dataclass
class Take:
    seconds: float
    cer: float
    heard: str
    tries: int
    passed: bool
    span: tuple[float, float] | None = None

    @property
    def spoken(self) -> float:
        return self.span[1] - self.span[0] if self.span else self.seconds


class ChatterboxEngine:
    def __init__(self) -> None:
        from chatterbox.tts import ChatterboxTTS

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Chatterbox on {self.device} ...", flush=True)
        self.model = ChatterboxTTS.from_pretrained(device=self.device)
        self.check = SpeechCheck(self.device)
        self.speaker: str | None = None

    @property
    def sample_rate(self) -> int:
        return self.model.sr

    def use_speaker(self, speaker: str) -> None:
        """Condition the model on one VCTK speaker; cheap to call again for the same one."""
        if speaker != self.speaker:
            ensure_refs([speaker])
            self.model.prepare_conditionals(str(ref_path(speaker)))
            self.speaker = speaker

    def _cut(self, wav: torch.Tensor, spoken: str, skip: int) -> tuple[torch.Tensor, tuple[float, float]] | None:
        """The part of a take that holds the script's words after the first `skip`.

        Cuts TRIM_LEAD/TRIM_TAIL outside the aligned words, but never further
        back than halfway into the pause after a context word, so none of it
        bleeds into the clip. None if the take cannot be aligned.
        """
        try:
            spans = self.check.word_spans(wav, self.sample_rate, spoken)
        except (ValueError, KeyError):
            return None
        start, end = spans[skip][0], spans[-1][1]
        cut_start = start - TRIM_LEAD
        if skip:
            cut_start = max(cut_start, (spans[skip - 1][1] + start) / 2)
        first = max(0, int(cut_start * self.sample_rate))
        last = min(wav.shape[-1], int((end + TRIM_TAIL) * self.sample_rate))
        return wav[first:last], (start, end)

    def say(self, speaker: str, text: str, dest: Path, seed: str,
            exaggeration: float = 0.5, cfg_weight: float = 0.5,
            candidates: int = 1, trim: bool = False, context: str = "") -> Take:
        """Render one line as a WAV at `dest`.

        exaggeration  0.25-1.0, how much emotion goes into the delivery
        cfg_weight    0.0-1.0, how tightly it follows the reference's pacing;
                      lower is slower and steadier, which offsets the rush that
                      high exaggeration brings with it
        candidates    passing takes to collect; with more than one, the one
                      with the shortest spoken span wins
        trim          cut the take down to its aligned words, so nothing comes
                      before the first word or lingers after the last; the
                      speech check then runs on what is left
        context       words spoken before `text` and cut away again (implies
                      trim). Chatterbox is shaky on one or two words with
                      nothing around them, so a short callout can be rendered
                      as "Notch! Notch!" and only the second one kept.
        """
        self.use_speaker(speaker)
        spoken = f"{context} {text}" if context else text
        skip = len(normalize_words(context))
        trim = trim or bool(context)
        max_seconds = SECONDS_PER_WORD_MAX * len(normalize_words(spoken)) + 1.0
        passing: list[tuple[torch.Tensor, Take]] = []
        best: tuple[float, torch.Tensor, Take] | None = None
        for attempt in range(MAX_TRIES + candidates - 1):
            torch.manual_seed(zlib.crc32(f"{speaker}|{seed}|{attempt}".encode()))
            wav = self.model.generate(spoken, exaggeration=exaggeration, cfg_weight=cfg_weight)
            wav = wav.detach().cpu().squeeze(0)
            seconds = wav.shape[-1] / self.sample_rate
            span = None
            if trim:
                cut = self._cut(wav, spoken, skip)
                if cut is not None:
                    wav, span = cut
            if trim and span is None:
                cer, heard = 1.0, "(could not align)"
            else:
                cer, heard = self.check.cer(wav, self.sample_rate, text)
            passed = seconds <= max_seconds and cer <= MAX_CER
            take = Take(seconds, cer, heard, attempt + 1, passed, span)
            if passed:
                passing.append((wav, take))
                if len(passing) >= candidates:
                    break
                continue
            score = cer + (0.0 if seconds <= max_seconds else 1.0)
            if best is None or score < best[0]:
                best = (score, wav, take)
            print(f"    ~ {speaker} try {attempt + 1}: {seconds:.1f}s (max {max_seconds:.1f}), "
                  f"CER {cer:.2f}, heard '{heard}'", flush=True)

        if passing:
            wav, take = min(passing, key=lambda p: p[1].spoken)
        else:
            _, wav, take = best
            print(f"    ! {speaker}: no clean take of '{text}', keeping the best (CER {take.cer:.2f})", flush=True)
        take.tries = attempt + 1
        sf.write(str(dest), wav.numpy(), self.sample_rate)
        return take
