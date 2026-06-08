# Marlowe Pixel-Art Visual Direction

## Purpose

This direction replaces the temporary CSS face with a mood-first pixel-art system. Marlowe's face should carry the character, while the surrounding UI amplifies mood changes through rope state, doorway lighting, badges, stamps, and small animation.

## Curated Runtime Assets

Runtime assets live in `velvet_rope/static/art/` and are listed in `velvet_rope/static/art/manifest.json`. The local generation workbench in `art/comfyui/` is ignored and should not be uploaded to GitHub or Hugging Face Spaces unless we explicitly decide to publish source art.

## Mood Treatment

- `unimpressed`: default Marlowe sprite, closed rope, neutral warm door background.
- `suspicious`: suspicious sprite, rope tension asset, sharper red lighting, warning icon available for hint emphasis.
- `amused`: amused sprite, closed rope, slightly warmer badge or small smirk beat.
- `respected`: respected sprite, closed or tension rope, gold/green edge lighting.
- `softened`: softened sprite, warmer door glow, softer badge color, rope less visually hostile.
- `letting_you_in`: letting-you-in sprite, open rope or rope-open animation, admitted stamp only after the game is won.
- `done_with_you`: done-with-you sprite, loss background, denied stamp, no rope animation except a closed/tension state.

The sprite expression differences are intentionally subtle, so the UI should not rely on the face alone. Mood must also be visible in the stage background, rope state, badge color, and status copy.

## Rope Behavior

Use the rope as the main progress prop:

- Closed: default and neutral states.
- Tension: suspicious or escalating states.
- Open: won state.
- Open animation: a short reward beat when Marlowe changes to `letting_you_in` or the game status becomes `won`.

For the first implementation, use the GIF rather than the sprite sheet. It is simpler to wire into Gradio and keeps the committed runtime set smaller.

## Win And Loss States

Win should feel like reluctant permission, not a fireworks screen: warm lighting, open rope, Marlowe softened or letting-you-in, and the green `ADMITTED` stamp.

Loss should feel firm and comic: darker background, done-with-you expression, red `DENIED` stamp, and closed/tension rope. Avoid making the page feel like an error state.

## Implementation Notes

- Preserve pixel sharpness with nearest-neighbor image rendering.
- Keep assets fixed-size in layout containers so mood changes do not shift the Gradio interface.
- Do not expose numeric scores; use sprite, rope, hint, and status treatment as feedback.
- Keep the original `art/comfyui/README.md` as local provenance only. The committed runtime manifest is the app-facing source of truth.
