# Rai — BETWEEN ORDER & CHAOS

AI-assisted animated music video production. Current status, findings and open questions are in
[`project/production_plan.md`](project/production_plan.md).

```bash
pip install librosa soundfile numpy scipy pillow
python3 project/music_analysis/analyze_music.py project/source_audio/<song> project/music_analysis/music_analysis.json
python3 project/procedural_effects/flower.py sheet out.png [reference|lightning|bridge]
python3 project/procedural_effects/flower.py morph out.mp4 [palette] [seconds]
```
