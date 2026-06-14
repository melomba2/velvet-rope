# Build Small Submission Checklist

Sources checked on June 14, 2026:

- https://huggingface.co/build-small-hackathon
- https://huggingface.co/spaces/build-small-hackathon/field-guide
- https://build-small-hackathon-field-guide.hf.space/submit
- https://build-small-hackathon-field-guide.hf.space/partners/openai
- https://build-small-hackathon-field-guide.hf.space/partners/modal

## Required Pre-flight

- [x] Under 32B: primary Gemma 4 12B path and Gemma 4 26B-A4B fallback are each under the
  32B total-parameter cap.
- [x] Gradio Space: deployed as `build-small-hackathon/velvet-rope`.
- [x] Source repo: https://github.com/melomba2/velvet-rope
- [x] Demo video: https://youtu.be/ilyFFChfPFE
- [x] Social post: https://x.com/lombard258/status/2065953865581596846
- [x] README tags: exact field-guide tags are in the README frontmatter.
- [x] README write-up: the README includes idea, tech, model accounting, runtime, and
  public artifact links.

## Official Tags Claimed

| Tag | Evidence |
| --- | --- |
| `track:wood` | Whimsical interactive AI game; the AI is the core character and persuasion loop. |
| `sponsor:openai` | Codex used across implementation, debugging, documentation, and submission prep; contributors and commit trailers make the use explicit. |
| `sponsor:modal` | Modal hosts the OpenAI-compatible llama.cpp service for the primary contest runtime. |
| `achievement:welltuned` | Five public character LoRA adapters specialize the 12B base model. |
| `achievement:offbrand` | Bespoke pixel-art UI, sprites, stamps, panels, and mood feedback go beyond stock Gradio styling. |
| `achievement:llama` | Primary runtime serves the model through llama.cpp. |
| `achievement:sharing` | Public cleaned playtest transcript dataset is linked from the README. |
| `achievement:fieldnotes` | `FIELD_NOTES.md` documents the build, small-model shape, Codex use, and shared artifacts. |

## Sponsor Readiness

- OpenAI: the field guide says Best Use of Codex requires Codex-attributed commits in the
  connected GitHub repo or Space. The final submission documentation commit should include
  a `Co-authored-by: OpenAI Codex <codex@openai.com>` trailer.
- Modal: the README names Modal as the runtime and includes the OpenAI-compatible Modal
  base URL pattern and Space variables.

## Not Claimed

- `track:backyard`: Velvet Rope is a whimsical game, not a practical daily-life app.
- `sponsor:openbmb`: no MiniCPM model is used.
- `sponsor:nvidia`: no Nemotron model is used.
- `achievement:offgrid`: the contest path uses Modal and an optional Hugging Face Router
  fallback.
- Tiny Titan: the core models are 12B and 26B-A4B, not <=4B.
- Best Agent: the app is character-driven and stateful, but not an agentic tool-use app.

## Final Verification Commands

```bash
python - <<'PY'
from pathlib import Path
import yaml

front = Path("README.md").read_text().split("---", 2)[1]
data = yaml.safe_load(front)
required = {
    "track:wood",
    "sponsor:openai",
    "sponsor:modal",
    "achievement:welltuned",
    "achievement:offbrand",
    "achievement:llama",
    "achievement:sharing",
    "achievement:fieldnotes",
}
missing = required - set(data["tags"])
assert not missing, missing
assert len(data["short_description"]) <= 60
PY

PYTHONPATH=. .venv/bin/pytest -q
hf spaces info build-small-hackathon/velvet-rope --format json
```
