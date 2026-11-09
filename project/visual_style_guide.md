# RAI — Visual Style Guide (v0.1, Phase 1)

## 1. Two light languages
The video is built on two kinds of light that meet.

| | Rai / lightning (energy) | Generative flower (structure) |
|---|---|---|
| Colour | Electric blue `#2E6BFF`, ice white `#EEF4FF`, silver `#C9D2E3` | As supplied: magenta-pink `#E36BB8`, hot white core `#FFF0FA` |
| Line character | Branching, sharp, momentary | Thin, looping, layered strand bundles; persistent |
| Motion | Impulse: fast attack, slow decay | Continuous: breathing, rotating, morphing |
| Meaning | Will, rupture, chaos | Order, perception, life |

Meeting colour: **subtle violet** `#8A63FF` / `#B79CFF`. When the two systems interact,
light mixes toward violet. TRANSCENDENCE is the most violet part of the film.
Base: midnight blue `#050A1F`, and near-black `#030208` from the flower reference's background.

*(Decision pending. See production_plan.md §6, Q2: keep the flower magenta as supplied, or shift it toward the blue palette.
Engine palettes `reference`, `lightning` and `bridge` exist in `procedural_effects/flower.py`.)*

## 2. Flower grammar (from `procedural_effects/flower_reference.jpg`)
- Thin 1–2 px strands, drawn as **bundles of slightly misregistered copies**. No solid fills.
- n-fold radial symmetry (the reference uses roughly 5–24 folds), nested teardrop petal loops, beaded rings
- White comes **only from line density** (additive light), never from painted white
- Many flowers at mixed scales; dark negative space between them (about 45% of the reference is near-black)
- Flowers overlap like transparent light, not solid objects
- Variety in the reference that should carry over: rosettes, tori (rings with empty centres), 3–5-arm "molecule" stars, gear-like scalloped rings

## 3. Order → chaos states (implemented as continuous parameters)
A Perfect symmetry · B Slight asymmetry · C Radial distortion · D Petal bifurcation ·
E Vortex formation · F Chaotic morphology · G Reorganized symmetry (new fold count, residual turbulence).
Preview: `procedural_effects/previews/flower_states_*.png`, `flower_morph_A_to_G.mp4`.

## 4. Cinematography
- 16:9, 1920×1080, 24 fps. Anime-film framing, with deliberate negative space for the flower.
- References are portrait. Rai shots must be **recomposed for 16:9, not cropped**. Keep her off-centre (thirds) with flower structures filling the other side.
- Lens feel: long lens (85–135 mm equivalent) for intimacy; wide (24 mm) only for scale shots.
- Depth: three planes of flowers (foreground blur, midground, background haze) plus volumetric haze.
- Lighting key: cool top/back rim from the lightning; violet fill bounced from the flowers; skin never lit warm except for faint blush.

## 5. Restraint rules
- Lightning is an event, not wallpaper. Big discharges are reserved for the measured energy peaks.
- At least one near-silent visual "breath" (≤10% screen luminance change for 2 s or more) per chapter
- No lens-flare spam, no fake text or HUD overlays, no stock fantasy elements (castles, swords, magic circles with runes)
