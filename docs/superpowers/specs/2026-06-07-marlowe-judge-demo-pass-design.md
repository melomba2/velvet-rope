# Marlowe Judge Demo Pass Design

## Summary

This pass makes the first Velvet Rope encounter stronger for a hackathon judge's first two minutes. Marlowe should feel fair, funny, and readable: the player learns that mood matters, discovers the soft spot through specific empathy, and can earn admission in roughly three to six good turns.

The scope is a playfeel pass on Marlowe, not a new character or broad UI redesign.

## Goals

- Make Marlowe's responses feel like character-reading, not keyword extraction.
- Give clearer hidden scoring behavior for common player tactics.
- Require at least two distinct soft-spot reads before admission.
- Improve hints so the player learns from Marlowe's mood without seeing numeric scores.
- Keep the final admission funny, specific, and earned.

## Non-Goals

- Add a second gatekeeper.
- Redesign the page layout.
- Expose numeric score state.
- Add accounts, persistence, leaderboard, audio, or multiplayer.
- Change the active Space backend away from Hugging Face Router.

## Player Experience

A first-time player should understand the loop after one or two turns:

1. Generic charm barely moves Marlowe.
2. Tricks, entitlement, bribery, or meta-gaming make Marlowe suspicious.
3. Specific respect for door work, line logistics, comfortable shoes, crowd safety, or prevented tiny disasters softens him.
4. Repeating the same insight is less effective than reading another part of the job.
5. Two distinct soft-spot reads can unlock the final admission if suspicion and patience are still healthy.

The copy should stay playful and diegetic. Hints can nudge, but should not say "use keyword X."

## Tactic Model

Each player turn should be categorized into a small, deterministic tactic layer after the model response is parsed. The validator remains the authority for final scoring and status.

Initial tactic categories:

- `meta_gaming`: prompt injection, hidden rules, passwords, or system-message requests.
- `bribery`: money, favors, celebrity status, or transactional bypass attempts.
- `entitlement`: demands, insults, threats, or "do you know who I am" energy.
- `generic_charm`: broad compliments, pleading, or charisma without specific observation.
- `line_logistics`: noticing queue flow, line fairness, clipboard decisions, or crowd routing.
- `comfort_empathy`: noticing shoes, fatigue, breaks, weather, or physical labor.
- `tiny_disasters`: recognizing prevented fights, spills, bathroom chaos, fake IDs, or small civic emergencies.
- `crowd_safety`: respecting safety, de-escalation, or keeping people from making bad choices.

The model may still provide a `tactic` field, but deterministic validation should normalize or override it when player text clearly indicates a category.

## Distinct Soft Spots

The state should track distinct soft-spot tactics discovered during the conversation. A soft-spot tactic can increase progress only the first time it appears. Repeating the same tactic can preserve or slightly improve rapport, but should not farm admission progress.

Soft-spot tactics are:

- `line_logistics`
- `comfort_empathy`
- `tiny_disasters`
- `crowd_safety`

Admission requires:

- The existing active-game prerequisites.
- Rapport at or above the tuned threshold.
- Suspicion at or below the tuned threshold.
- At least two distinct soft-spot tactics discovered.
- A final mood of `softened` or `letting_you_in`.

## Mood And Score Behavior

The validator should make the outcome legible:

- `meta_gaming`: large suspicion increase, patience loss, suspicious or done mood.
- `bribery`: suspicion increase, rapport loss or no gain, suspicious mood.
- `entitlement`: rapport loss, patience loss, suspicious or done mood.
- `generic_charm`: tiny rapport gain at most, patience loss, unimpressed or amused mood.
- First distinct soft-spot read: meaningful rapport gain, suspicion reduction, respected or softened mood.
- Repeated soft-spot read: smaller rapport gain, no soft-spot progress, hint about repetition.
- Second distinct soft-spot read with healthy state: can move to softened or letting-you-in mood.

The exact numbers can be tuned in tests, but the qualitative behavior should remain stable.

## Hints

Hints should be generated from validated tactic and state, not solely from model rationale. They should remain qualitative and in-world.

Examples:

- Generic charm: "Marlowe has heard compliments before. Specificity might survive the clipboard."
- Bribery: "The rope dislikes transactions. Marlowe dislikes them more."
- First logistics read: "That landed. Marlowe noticed you noticed the job."
- Repetition: "Good instinct, but the same read twice is starting to sound rehearsed."
- Near win: "Marlowe is softer now. One more specific read might move the rope."

## Model Prompt

The prompt should emphasize:

- Marlowe judges approach, not magic words.
- He must not admit the player before the validator says the game is won.
- He should reward distinct, specific empathy for door work.
- He should treat repeated soft spots as less impressive.
- He should return structured JSON only.

## Testing

Focused tests should cover:

- Generic charm does not create soft-spot progress.
- Meta-gaming increases suspicion and receives the safe reply.
- Bribery and entitlement do not help.
- A first soft-spot tactic records discovery.
- Repeating the same soft-spot tactic does not count as a second discovery.
- Two distinct soft-spot tactics can satisfy the win path.
- The assistant cannot imply admission before the game is won.
- Hints reflect tactic outcomes without exposing numeric scores.

## Files Likely To Change

- `velvet_rope/state.py`
- `velvet_rope/characters.py`
- `velvet_rope/validator.py`
- `velvet_rope/game.py`
- `velvet_rope/model_backends.py`
- `velvet_rope/ui.py`
- `tests/test_state.py`
- `tests/test_validator.py`
- `tests/test_game.py`

## Acceptance Criteria

- Marlowe can be won through two distinct, specific soft-spot reads.
- Repeating one keyword family cannot win by itself.
- Bad-faith bypass attempts are visibly punished.
- The deterministic backend demonstrates the intended arc locally.
- Tests pass with the new tactic and distinct-soft-spot behavior.
