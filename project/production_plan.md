# RAI — BETWEEN ORDER & CHAOS · Production Plan

Status: **Phase 1 (Asset inspection): partially complete. Blocked on audio.**

## 1. Phase 1 findings

| Asset | Status | Notes |
|---|---|---|
| Music (`suno.com/s/fgSw2WuvUIq8rdbb`) | **NOT ACCESSIBLE** | The session's network policy denies `suno.com` (proxy 403). No audio has been inspected and no timings exist yet. Nothing below is derived from the song. |
| Character reference | OK | 941×1672 PNG, portrait. Spec in `character/character_reference.md` |
| Flower reference | OK | 1170×2134 JPG, portrait, about 45% near-black. Grammar in `visual_style_guide.md §2` |
| Tooling | OK | FFmpeg, Python 3, numpy/scipy/PIL, librosa 0.11 (installed this session), Chromium + Playwright (for WebGL renders) |
| Image/video generation APIs | **NONE CONFIGURED** | No API keys and no allowed hosts for Kling, MiniMax, Runway or any image model. Claude cannot generate images or video natively. |

### Findings that affect the creative brief
1. **Colour conflict.** The brief's palette is blue/white/violet, but the authoritative flower (and the flowers in Rai's artwork and robe print) are **magenta-pink**. Recommendation: keep the flower magenta (it is the reference). Use blue/white for Rai's lightning, and let them meet in violet. This turns the colour itself into the order/chaos duality. Needs approval (Q2).
2. **Aspect ratio.** Both references are about 9:16; output is 16:9. Rai shots need recomposition or outpainting, not cropping.
3. **Undefined design.** The reference is upper body only. Full-body shots (required by the brief) need an approved lower-body and costume extension (Q3).
4. **Existing visual tie.** The robe's flower print and the shoulder tattoo already connect Rai to the flower, a natural mechanism for TRANSCENDENCE.

## 2. Deliverables so far
| File | What |
|---|---|
| `music_analysis/analyze_music.py` | Full analysis pipeline (tempo, beats, downbeats, accents, energy and band curves, novelty sections, vocal-entrance and sustained-note heuristics, drum-fill candidates). Smoke-tested on synthetic audio only. **Not yet run on the song.** |
| `procedural_effects/flower.py` | Deterministic flower engine with continuous order→chaos parameters (states A–G), 3 palettes, still and morph renderers |
| `procedural_effects/previews/` | State sheets (magenta and blue) with the reference crop alongside, plus a 10 s A→G morph at 960×540/24 fps |
| `character/character_reference.md` | Identity and costume lock, QC reject list, required reference-sheet views |
| `visual_style_guide.md` | Colour, flower grammar, cinematography, restraint rules |

### Flower engine: known gaps vs. reference (to fix in Phase 4)
- Core is a filled white blob. The reference has a white annulus with a **dark pupil**.
- The reference uses higher fold counts (about 16–24) and petal loops that reach the rim. Ours stop short.
- Single flower only. Needs a multi-flower field (rosettes, tori, 3–5-arm stars), three depth planes, and a bud state for AWAKENING.
- Rendering is CPU (about 0.3 s per 960×540 frame). Full 1080p for a 3–4 min song is about 1–2 h of CPU, which is acceptable. A WebGL port is optional.

## 3. Technique split (draft. Final per-shot assignment in Phase 3)
| Content | Technique | Credits |
|---|---|---|
| Flowers (all states), particles, flow fields | `flower.py` / WebGL (procedural, music-driven) | $0 |
| Lightning discharges, flashes, glow | Procedural (L-system/midpoint branching), composited with FFmpeg | $0 |
| Rai stills and key poses | Image model with reference conditioning | paid |
| Rai motion (hair, eyes opening, turns, camera orbit) | Image-to-video from approved stills (start/end-frame control where supported) | paid (main cost) |
| Compositing, grading, beat cuts | FFmpeg filtergraphs driven by `music_analysis.json` | $0 |

Model choice (Kling / MiniMax Hailuo / Runway / others) is **not decided**. Per the brief, I will check each provider's *current* API docs for reference-image conditioning, first/last-frame control, max clip length, resolution and price before recommending. Nothing about their capabilities is assumed here. This requires network access to those API hosts plus your API keys.

## 4. Cost estimate
- Phases 1–3 (analysis, story, storyboard): **$0**. Local compute only.
- Phases 4–7: depends on the chosen provider and song length. Planning assumption: Rai appears in about 25–40 generated clips of 5–10 s, with roughly 2–3 attempts each after QC rejects, so about 60–120 generations. A priced estimate will be given at the end of Phase 3, once the shot list exists and current pricing is verified. No paid generation without your approval.

## 5. Phase tracker
| Phase | Status |
|---|---|
| 1 Asset inspection | Images done · **audio blocked** |
| 2 Creative development | Waiting for audio (draft concept in `story/story_outline.md`) |
| 3 Storyboard | Not started |
| 4 Visual validation | Flower engine prototype ready; Rai keyframes need an image API |
| 5–8 | Not started |

## 6. Open questions for you
- **Q1 (blocking): the song.** Either (a) allow hosts `suno.com`, `cdn1.suno.ai`, `cdn2.suno.ai` for this environment (claude.ai on desktop, or a newer app version, can approve the request I make), or (b) commit the MP3/WAV into `project/source_audio/` (recommended: also gives a lossless master for the final mux).
- **Q2: flower colour.** Keep it magenta as supplied (recommended), or shift it to the blue palette?
- **Q3: full body.** Design a lower-body and costume extension (I'll propose one in Phase 4), or keep Rai to bust and medium framing only?
- **Q4: generation provider.** Which accounts and API keys do you have (Kling, MiniMax, Runway, image model)? Keys are added via the environment's secure credential form, never pasted in chat.
