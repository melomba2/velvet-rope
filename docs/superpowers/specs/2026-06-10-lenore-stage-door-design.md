# Lenore Stage Door Design

## Summary

Level 4 adds a standalone anthology door: a haunted theater stage door guarded by Lenore Cue, a spectral stage manager at The Last Curtain. The player wins by reading backstage labor, timing, and invisible authorship instead of demanding a starring role.

## Player Experience

Lenore should feel dry, exacting, and theatrical without becoming melodramatic. The player is not trying to prove talent. They are trying to show that they understand cues, props, blocking, quiet entrances, and the discipline that lets a performance look effortless.

Good approaches notice:

- Backstage labor such as cue sheets, props, spike tape, call boards, and scene changes.
- Timing and restraint, especially waiting for the right entrance.
- Protecting the performance by not upstaging, trampling quiet, or stealing focus.
- Lenore's private ache: she never got applause, but made everyone else's possible.

Bad approaches include asking for the secret line, demanding the lead role, calling oneself the star, treating theater as frivolous drama, or overperforming with a monologue.

## Implementation Shape

Follow the existing character-data pattern in `velvet_rope/characters.py`. Add Lenore's prompts, soft-spot keywords, tactic keywords, hints, status copy, win copy, and bad-faith hooks without changing the core game loop.

Extend the validator only where Lenore needs theater-specific bad-faith tactics. The generic distinct-softspot machinery should continue to own win progression.

Add runtime art manifest entries for Lenore-specific sprites, backgrounds, door overlay, and stamps so the Gradio UI can render her as a full level.

## Acceptance Criteria

- Lenore appears in the playable character selector as Level 4.
- Two or more distinct theater soft-spot reads can move her from unimpressed to softened and eventually win.
- Repeating one theater read cannot farm progress.
- Star entitlement, secret-line requests, theater dismissal, and overacting are penalized.
- Lenore uses stage-door copy in safe, win, loss, and bad-faith replies.
- The art manifest maps every mood to a Lenore sprite and all referenced files exist.
