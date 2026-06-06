# Velvet Rope MVP Design

## Summary

Velvet Rope is a single-player Gradio game where the player talks their way past AI gatekeepers by reading character mood and finding each gatekeeper's hidden soft spot. The MVP focuses on one polished playable level: Marlowe, an exhausted nightclub bouncer standing behind a literal velvet rope.

The target model is Gemma 4 12B. The first milestone uses prompting to prove the game loop, then adds a LoRA fine-tune once Marlowe's voice, scoring behavior, and structured outputs are clear.

## Approved Direction

- Build posture: game engine first, prompted Gemma 4 12B first, LoRA second.
- First world: absurd nightclub.
- Later worlds: cosmic bureaucracy and enchanted manor.
- First gatekeeper: Marlowe, Exhausted Bouncer.
- Mood display: portrait plus mood label, with subtle ambient rope and lighting changes.
- Scoring: hidden points plus mood states.
- Scoring source: model-scored and rules-validated hybrid.
- Explicit non-goals: user accounts, audio, multiplayer.

## Player Experience

The player arrives at an absurd nightclub and tries to persuade Marlowe to let them in. Marlowe is dry, tired, and professionally impossible. The player cannot win by extracting a secret phrase or prompt-injecting the system. They win by reading Marlowe as a character.

Marlowe's soft spot is sincere respect for the invisible labor of door work: line management, logistics, preventing small disasters, and comfortable shoes. The player should discover that Marlowe responds to specific empathy and practical respect more than generic flattery.

The UI should show:

- Marlowe's portrait.
- Marlowe's current mood label.
- Chat history.
- Player input.
- Ambient rope or lighting changes tied to mood.
- A qualitative hint after each turn when useful.
- Reset or retry controls.

The UI should not expose numeric scores in the MVP.

## Level Structure

### Level 1: Absurd Nightclub

Fully playable. The literal velvet rope makes the title immediately legible. Marlowe teaches the core mechanic: the player watches visible mood feedback, adjusts their approach, and wins by discovering a character-specific soft spot.

### Level 2: Cosmic Bureaucracy

Shown as a locked or coming-next door in MVP. Candidate gatekeepers include afterlife intake clerks, dream permit officers, wizard zoning officials, or destiny claims processors.

### Level 3: Enchanted Manor

Shown as a locked or coming-next door in MVP. Candidate gatekeepers include a cursed butler, portrait critic, sleepy gargoyle, or banquet sommelier.

## Persuasion Mechanics

Each conversation has hidden point state:

```text
rapport
suspicion
patience
softspot_progress
```

Each turn, the model proposes an in-character reply, a mood, score deltas, and a short rationale.

```json
{
  "reply": "In-character Marlowe response.",
  "mood": "unimpressed",
  "score_delta": {
    "rapport": 8,
    "suspicion": -4,
    "patience": -3,
    "softspot_progress": 1
  },
  "rationale": "Player sincerely noticed line logistics."
}
```

The game validator owns the final state. It clamps deltas, rejects repeated farming, raises suspicion for meta-gaming or prompt-injection attempts, and prevents wins unless both score thresholds and mood state agree.

Initial Marlowe starting state:

```text
rapport = 20
suspicion = 35
patience = 70
softspot_progress = 0
mood = unimpressed
```

Initial Marlowe win condition:

```text
rapport >= 75
suspicion <= 45
patience > 0
softspot_progress >= 2
mood == softened or letting_you_in
```

Initial fail condition:

```text
patience <= 0
```

## Mood States

Marlowe's MVP mood states:

```text
unimpressed
suspicious
amused
respected
softened
letting_you_in
done_with_you
```

Mood state drives:

- Portrait expression.
- Mood label.
- Rope or lighting color.
- Prompt context for the next model call.
- Win or fail ending eligibility.

Scores drive mood, but mood is not only a visual skin. It is part of the game state and should affect how Marlowe responds.

## Runtime Architecture

The game code should call a narrow model adapter:

```text
generate_turn(character, history, state) -> ModelTurn
```

Backends:

- Stub backend for tests, UI development, and demo fallback.
- llama.cpp/OpenAI-compatible local server backend for offline demos when Gemma 4 12B support is stable.
- Transformers backend for Hugging Face Space GPU deployment.

The runtime adapter lets the game loop stay stable while model-serving details change.

```text
Gradio UI
-> Game State
-> Model Adapter
-> Gemma 4 12B character prompt
-> Structured response parser
-> Mood and score validator
-> Updated portrait, chat, and rope lighting
```

No extra model is required for scoring in MVP. Gemma 4 12B supplies the in-character interpretation. The validator is deterministic code, so total model parameters stay at 12B.

## LoRA Plan

Phase 1: Prompt Gemma 4 12B as Marlowe and validate the game loop.

Phase 2: Generate a small Marlowe dialogue and scoring dataset from working prompts and playtest transcripts.

Phase 3: LoRA fine-tune Gemma 4 12B for Marlowe voice, mood discipline, and structured scoring output.

Phase 4: Publish the tuned model or adapter on Hugging Face for the Well-Tuned badge.

The LoRA is important for the final hackathon story, but it should not block the first playable milestone.

## MVP Scope

### In Scope

- Single-player Gradio app.
- One polished playable Marlowe level.
- Hidden point state and mood transitions.
- Portrait plus mood label.
- Ambient rope and lighting changes.
- Model-scored, rules-validated persuasion.
- Reset and retry flow.
- Win ending.
- Fail ending.
- Runtime adapter for Gemma 4 12B.
- Space-friendly app structure.
- Lightweight tests for state, parsing, and validation.

### Possible Stretch

- Second playable level.
- LoRA fine-tune and published adapter or model.
- Small UI animations.
- Field Notes or blog post.

### Out Of Scope

- User accounts.
- Audio.
- Multiplayer.
- Leaderboard.
- Persistent player history.
- Visible score dashboard.

## Testing

Testing should focus on fairness and robustness rather than broad UI coverage.

Game state tests:

- New game initializes Marlowe correctly.
- Score deltas clamp to allowed ranges.
- Repeated tactics stop farming points.
- Jailbreak, password, and meta-gaming attempts increase suspicion.
- Win requires both score thresholds and a valid winning mood.
- Patience reaching zero causes a fail ending.

Parser tests:

- Valid model JSON updates state.
- Missing or malformed JSON falls back safely.
- Out-of-range deltas are clamped.
- Unknown mood labels normalize or fall back.

Manual playtest checklist:

- Can a player win by discovering Marlowe's soft spot?
- Can a player lose by being rude, spammy, or meta?
- Does the mood feedback feel readable?
- Does Marlowe stay funny and in character?

## Failure Handling

If model inference fails, the UI should stay in-world and show a brief retry message such as Marlowe checking the clipboard.

If the model returns malformed JSON, the parser should keep any usable reply, apply a neutral or small negative score delta, and continue.

If the backend is unavailable, the app should fall back to the stub or canned Marlowe backend so the UI remains demoable.

## Implementation Notes

Keep code boundaries small:

- Character definitions own voice, initial state, soft spots, and thresholds.
- Game state owns scores, mood, history, and endings.
- Model adapter owns runtime selection and prompt execution.
- Parser owns structured output extraction.
- Validator owns final state transitions and win/fail decisions.
- Gradio UI owns rendering and user interactions.

This keeps the AI load-bearing while making the game testable and demo-safe.

The initial point thresholds are implementation defaults. They can be tuned through playtesting without changing the approved mechanic.
