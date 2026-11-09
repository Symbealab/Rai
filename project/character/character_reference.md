# Rai — Character Reference Specification (v0.1, Phase 1)

Authoritative source: `character/refs/rai_reference.png` (941×1672, portrait ≈ 9:16).
Everything below is read off that image. Where the image does not show something
(legs, back, full figure), the item is marked **UNDEFINED**. Undefined items need an
approved design extension before any full-body or back shot is generated.

## 1. Identity lock (never changes)

| Attribute | Spec (from reference) |
|---|---|
| Age presentation | Young adult |
| Overall style | High-detail painterly anime render: soft skin shading, crisp line accents, glossy highlights, rim light |
| Face shape | Slim oval, delicate pointed chin, narrow jaw, small straight nose |
| Eyes | Almond-shaped, heavy-lidded and half-closed, long lower lashes. Irises pale lilac-grey shading to blue-violet, with soft highlights |
| Gaze | Calm and detached, looking down along the nose (head tilted back) |
| Brows | Thin and soft, mostly hidden by bangs |
| Lips | Soft rose-pink, slightly parted, full lower lip |
| Skin | Porcelain-pale with cool violet ambient shadows and faint warm blush on cheeks |
| Marks | Small dark beauty mark and faint red dots under the eye on the image-left side. **Keep consistent: this mark anchors her identity.** |
| Hair length | Short, layered and choppy. Nape and side strands reach the jaw/neck; a few wisps fall to the collar |
| Hair colour | Silver-white highlights, periwinkle/electric-blue mid-tones, deep blue-violet in shadow. Strands are fine and separated, flying outward like static discharge |
| Bangs | Long and asymmetric, swept across the brow and partly veiling the image-left eye |

## 2. Costume & accessories lock

| Item | Spec |
|---|---|
| Top | Black sleeveless top with a high mandarin/halter collar. Image-right shoulder fully bare |
| Outer layer | Black jacket/robe slipping off the shoulders. Fabric is **printed with the generative flower motif** (pink/violet line-art) and trimmed with gold piping |
| Sheer layer | Translucent, iridescent ribbons/shawl (white-lilac) wrapping around the torso and flowing outward |
| Neck | Gold chain collar of interlocking loops. A circular disc pendant (ring/gear form) with long drop chains ending in elongated gold bar pendants |
| Ears | Both ears: gold multi-hoop ear cuffs plus long drop earrings (hoop, then a rectangular bar) |
| Tattoo | Image-right upper arm and shoulder: fine-line tattoo of circles, flowers and gears with small red accents. It echoes the flower system |
| Lower body / footwear | **UNDEFINED** |
| Hands | **UNDEFINED** (not visible). Nail style is unknown |

> Story note: the flower print on her robe and the tattoo already tie Rai to the
> generative flower in the source art. Use this tie, don't invent a new link.
> In TRANSCENDENCE the printed flowers and the tattoo can light up and lift off the fabric.

## 3. Things to avoid (QC reject list)
- Hair turning long, straight, single-colour, or anime-flat cel blue
- Eye colour drifting to saturated red, gold, or flat blue; eyes opening wide "moe" style in neutral shots
- Losing the beauty mark, or the mark moving to the other side
- Collar turning into a V-neck; the bare shoulder or the tattoo swapping sides
- Gold jewellery turning into silver, or chains disappearing between shots
- Extra characters, or Rai's face appearing on background figures
- Mirrored (flipped) generations. **Check the mark, tattoo and bang side on every shot.**

## 4. Reference sheet: to be generated in Phase 4 (needs an image model, see production_plan.md)
Required views, all conditioned on `rai_reference.png`:
1. Front, neutral, bust (eyes fully open, for lip-sync-free close-ups)
2. Three-quarter (matches the reference angle)
3. Side profile, both directions (left and right profile, kept separate because of asymmetry)
4. Extreme close-up of the eyes (open, half-lidded, closed). Used by RAI-001 "eyes open on accent"
5. Expressions: serene (default), determined, released or exhilarated (EXPLOSION), fragile with wet eyes (FRAGILITY), peaceful smile (REBIRTH)
6. Neutral standing pose: **requires a full-body design extension (UNDEFINED lower body)**
7. Dynamic pose: arms spread, hair and ribbons in an updraft (EXPLOSION key pose)

Every sheet image must pass Section 3 before it becomes a conditioning reference itself.
