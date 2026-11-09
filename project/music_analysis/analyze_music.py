#!/usr/bin/env python3
"""RAI — music analysis.

Derives the song structure from the actual audio (no assumed pop form):
tempo/beat grid, downbeats estimate, onset accents, RMS energy curve,
spectral bands (low/mid/high) for visual drivers, novelty-based section
boundaries, vocal-presence estimate (harmonic/percussive + mid-band
flatness heuristic), sustained-note candidates and dynamic peaks.

Usage:
    python3 analyze_music.py <audio file> [out.json]

Section *labels* (verse/chorus/...) are suggested from energy + repetition
and must be reviewed by ear; boundaries and timings are measured.
"""
import json
import sys

import librosa
import numpy as np

SR = 22050
HOP = 512


def t(frames):
    return librosa.frames_to_time(frames, sr=SR, hop_length=HOP)


def smooth(x, n):
    if n <= 1:
        return x
    k = np.hanning(n)
    k /= k.sum()
    return np.convolve(x, k, mode="same")


def main(path, out):
    y, sr = librosa.load(path, sr=SR, mono=True)
    dur = len(y) / sr
    y_h, y_p = librosa.effects.hpss(y)

    # --- tempo & beats -------------------------------------------------
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=HOP)
    tempo = float(np.atleast_1d(tempo)[0])
    beat_times = t(beats)
    # downbeat estimate: choose the phase (0..3) whose beats carry most low-end energy
    S = np.abs(librosa.stft(y, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=sr)
    low = S[freqs < 150].sum(0)
    mid = S[(freqs >= 150) & (freqs < 2500)].sum(0)
    high = S[freqs >= 2500].sum(0)
    phase_score = [low[beats[p::4]].mean() if len(beats[p::4]) else 0 for p in range(4)]
    phase = int(np.argmax(phase_score))
    downbeats = beat_times[phase::4]

    # --- energy ----------------------------------------------------------
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    rms_s = smooth(rms, int(sr / HOP * 2))  # ~2 s window
    rms_n = rms_s / (rms_s.max() + 1e-9)

    # --- accents (strong onsets, percussive) ---------------------------
    p_env = librosa.onset.onset_strength(y=y_p, sr=sr, hop_length=HOP)
    acc = librosa.onset.onset_detect(onset_envelope=p_env, sr=sr, hop_length=HOP, units="frames")
    thr = np.percentile(p_env[acc], 90) if len(acc) else 0
    strong = acc[p_env[acc] >= thr]

    # --- sections: recurrence + novelty ---------------------------------
    chroma = librosa.feature.chroma_cqt(y=y_h, sr=sr, hop_length=HOP)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=HOP, n_mfcc=13)
    feat = np.vstack([librosa.util.normalize(chroma, axis=0), librosa.util.normalize(mfcc, axis=1)])
    feat_sync = librosa.util.sync(feat, beats, aggregate=np.median)
    n_seg = int(np.clip(round(dur / 20), 6, 14))
    bounds_beats = librosa.segment.agglomerative(feat_sync, n_seg)
    bfr = librosa.util.fix_frames(beats[np.clip(bounds_beats, 0, len(beats) - 1)], x_min=0, x_max=len(rms) - 1)
    btimes = sorted(set(np.round(t(bfr), 2).tolist() + [round(dur, 2)]))
    # merge sections shorter than ~2 bars into their predecessor
    min_len = max(4.0, 8 * 60 / max(tempo, 1))
    merged = [btimes[0]]
    for b in btimes[1:]:
        if b - merged[-1] < min_len and b != btimes[-1]:
            continue
        merged.append(b)
    if len(merged) > 2 and merged[-1] - merged[-2] < min_len:
        merged.pop(-2)
    btimes = merged

    # vocal-presence heuristic: harmonic mid band vs. total, per frame
    Sh = np.abs(librosa.stft(y_h, hop_length=HOP))
    voc_band = Sh[(freqs >= 300) & (freqs < 3400)].sum(0)
    flat = librosa.feature.spectral_flatness(y=y_h, hop_length=HOP)[0]
    voc = smooth(voc_band / (S.sum(0) + 1e-9) * (1 - flat), int(sr / HOP))
    voc_n = (voc - voc.min()) / (np.ptp(voc) + 1e-9)

    # segment-level similarity for repetition-based labelling
    seg_feats = []
    for a, b in zip(btimes[:-1], btimes[1:]):
        fa, fb = librosa.time_to_frames([a, b], sr=sr, hop_length=HOP)
        seg_feats.append(chroma[:, fa:max(fb, fa + 1)].mean(1))
    seg_feats = np.array(seg_feats)
    sim = seg_feats @ seg_feats.T / (np.linalg.norm(seg_feats, axis=1)[:, None] * np.linalg.norm(seg_feats, axis=1)[None] + 1e-9)

    sections = []
    for i, (a, b) in enumerate(zip(btimes[:-1], btimes[1:])):
        fa, fb = librosa.time_to_frames([a, b], sr=sr, hop_length=HOP)
        fb = max(fb, fa + 1)
        e = float(rms_n[fa:fb].mean())
        v = float(voc_n[fa:fb].mean())
        rep = int(((sim[i] > 0.97).sum()) - 1)
        sections.append({
            "index": i, "start": round(a, 2), "end": round(b, 2), "duration": round(b - a, 2),
            "energy": round(e, 3), "vocal_presence": round(v, 3), "repeats_elsewhere": rep,
            "low": round(float(low[fa:fb].mean() / low.max()), 3),
            "high": round(float(high[fa:fb].mean() / high.max()), 3),
        })
    # suggested labels (to be confirmed by listening)
    es = np.array([s["energy"] for s in sections])
    hi, lo = np.percentile(es, 70), np.percentile(es, 35)
    for i, s in enumerate(sections):
        if i == 0 and s["energy"] < hi:
            lab = "intro"
        elif i == len(sections) - 1 and s["energy"] < hi:
            lab = "outro"
        elif s["energy"] >= hi:
            lab = "chorus_candidate"
        elif s["energy"] <= lo:
            lab = "break_or_bridge_candidate"
        elif i + 1 < len(sections) and sections[i + 1]["energy"] >= hi:
            lab = "pre_chorus_candidate"
        else:
            lab = "verse_candidate"
        if s["vocal_presence"] < 0.25 and lab not in ("intro", "outro"):
            lab += "_instrumental"
        s["suggested_label"] = lab

    # --- events ----------------------------------------------------------
    peaks = librosa.util.peak_pick(rms_n, pre_max=200, post_max=200, pre_avg=200, post_avg=200, delta=0.05, wait=400)
    # sustained notes: long low-onset stretches with high harmonic energy
    h_rms = smooth(librosa.feature.rms(y=y_h, hop_length=HOP)[0], 20)
    calm = smooth(onset_env, 40) < np.percentile(onset_env, 40)
    sustained, start = [], None
    for f, c in enumerate(calm & (h_rms > np.percentile(h_rms, 60))):
        if c and start is None:
            start = f
        elif not c and start is not None:
            if t(f) - t(start) >= 1.5:
                sustained.append([round(float(t(start)), 2), round(float(t(f)), 2)])
            start = None
    # vocal entrances: rising edges of vocal presence
    vmask = voc_n > 0.45
    entr = np.where(vmask[1:] & ~vmask[:-1])[0]
    entr = [round(float(x), 2) for x in t(entr)]
    entr = [x for i, x in enumerate(entr) if i == 0 or x - entr[i - 1] > 2.0]
    # drum fills: dense percussive onsets in the bar before a section boundary
    fills = []
    for b in btimes[1:-1]:
        win = [x for x in t(acc) if b - 2.0 <= x < b]
        if len(win) >= 6:
            fills.append({"before_boundary": b, "onsets_in_2s": len(win)})

    curve_hz = 4  # downsampled curves for the visual engine
    tt = np.arange(0, dur, 1 / curve_hz)
    fr = librosa.time_to_frames(tt, sr=sr, hop_length=HOP).clip(0, len(rms) - 1)

    def norm(x):
        x = smooth(x, int(sr / HOP / curve_hz))
        return (x / (np.percentile(x, 99) + 1e-9)).clip(0, 1)

    result = {
        "source": path, "duration_sec": round(dur, 3), "sample_rate": sr,
        "tempo_bpm": round(tempo, 2), "beat_count": int(len(beats)),
        "beats": np.round(beat_times, 3).tolist(),
        "downbeats_estimated": np.round(downbeats, 3).tolist(),
        "strong_accents": np.round(t(strong), 3).tolist(),
        "energy_peaks": np.round(t(peaks), 3).tolist(),
        "vocal_entrances_estimated": entr,
        "sustained_note_candidates": sustained,
        "drum_fill_candidates": fills,
        "sections": sections,
        "curves": {
            "hz": curve_hz, "time": np.round(tt, 3).tolist(),
            "energy": np.round(rms_n[fr], 3).tolist(),
            "low": np.round(norm(low)[fr], 3).tolist(),
            "mid": np.round(norm(mid)[fr], 3).tolist(),
            "high": np.round(norm(high)[fr], 3).tolist(),
            "vocal": np.round(voc_n[fr], 3).tolist(),
        },
        "notes": "Boundaries/timings measured. suggested_label and vocal estimates are heuristics; confirm by listening before locking the storyboard.",
    }
    with open(out, "w") as f:
        json.dump(result, f, indent=1)
    print(f"duration {dur:.1f}s  tempo {tempo:.1f} BPM  beats {len(beats)}  sections {len(sections)}")
    for s in sections:
        print(f"  {s['start']:7.2f}-{s['end']:7.2f}  E={s['energy']:.2f} V={s['vocal_presence']:.2f}  {s['suggested_label']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "music_analysis.json")
