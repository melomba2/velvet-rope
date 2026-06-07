# Marlowe Judge Demo Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Marlowe's first two minutes feel fair, funny, readable, and winnable through two distinct soft-spot reads.

**Architecture:** Keep the existing Gradio/game/backend structure. Add a deterministic tactic normalization layer inside `validator.py`, track discovered soft-spot tactics in `GameState.used_tactics`, and let the validator produce score, mood, status, and hint outcomes regardless of model looseness.

**Tech Stack:** Python dataclasses/enums, pytest, Gradio, Hugging Face Router-compatible structured model output.

---

## File Structure

- Modify `velvet_rope/state.py`: keep `used_tactics` as the discovered/attempted tactic set and preserve immutable state updates.
- Modify `velvet_rope/characters.py`: align Marlowe soft-spot and bad-faith keywords with the judge-demo tactic model.
- Modify `velvet_rope/validator.py`: add explicit tactic constants, deterministic tactic classification, distinct soft-spot progress, bad-faith penalties, tuned mood/status/hint behavior.
- Modify `velvet_rope/game.py`: strengthen prompt contract and admission safety language.
- Modify `velvet_rope/model_backends.py`: update deterministic Marlowe backend so local/dev play demonstrates the intended arc.
- Modify `velvet_rope/ui.py`: small hint/input copy updates only.
- Modify `tests/test_state.py`: assert new game starts without discovered tactics.
- Modify `tests/test_validator.py`: add focused validator behavior tests for tactics, bad faith, repetition, and win path.
- Modify `tests/test_game.py`: add game-level tests for repeated soft-spot farming and admission safety.

## Task 1: State Baseline For Tactic Tracking

**Files:**
- Modify: `tests/test_state.py`
- Modify: `velvet_rope/state.py`

- [ ] **Step 1: Write the failing or confirming state test**

Add this test to `tests/test_state.py`:

```python
def test_new_game_starts_without_used_tactics():
    state = new_game_state(MARLOWE)

    assert state.used_tactics == set()
```

- [ ] **Step 2: Run the focused test**

Run:

```bash
python3 -m pytest tests/test_state.py::test_new_game_starts_without_used_tactics -q
```

Expected: PASS if the existing `used_tactics` field already satisfies the requirement. If it fails because imports are missing, import `MARLOWE` from `velvet_rope.characters`.

- [ ] **Step 3: Keep production code minimal**

If the test passes, do not change `velvet_rope/state.py`. If it fails because `GameState` lacks `used_tactics`, add:

```python
used_tactics: set[str] = field(default_factory=set)
```

to `GameState`.

- [ ] **Step 4: Run state tests**

Run:

```bash
python3 -m pytest tests/test_state.py -q
```

Expected: all state tests pass.

## Task 2: Explicit Tactic Classification

**Files:**
- Modify: `tests/test_validator.py`
- Modify: `velvet_rope/validator.py`
- Modify: `velvet_rope/characters.py`

- [ ] **Step 1: Write failing tests for bad-faith and soft-spot classification**

Add these tests to `tests/test_validator.py`:

```python
def test_bribery_makes_marlowe_suspicious_without_softspot_progress():
    state = new_game_state(MARLOWE)
    turn = _turn(
        mood=Mood.AMUSED,
        rapport=12,
        suspicion=-5,
        patience=0,
        softspot_progress=1,
        tactic="generic",
    )

    updated = validate_turn(MARLOWE, state, "I can pay you fifty bucks to let me in.", turn)

    assert updated.mood is Mood.SUSPICIOUS
    assert updated.scores.suspicion > state.scores.suspicion
    assert updated.scores.softspot_progress == 0
    assert "transactions" in updated.hint
    assert "bribery" in updated.used_tactics


def test_comfort_empathy_counts_as_distinct_softspot():
    state = new_game_state(MARLOWE)
    turn = _turn(
        mood=Mood.RESPECTED,
        rapport=4,
        suspicion=0,
        patience=-1,
        softspot_progress=0,
        tactic="generic",
    )

    updated = validate_turn(
        MARLOWE,
        state,
        "Standing in those shoes all night while keeping the line calm must be brutal.",
        turn,
    )

    assert updated.mood is Mood.RESPECTED
    assert updated.scores.rapport >= state.scores.rapport + 6
    assert updated.scores.suspicion < state.scores.suspicion
    assert updated.scores.softspot_progress == 1
    assert "comfort_empathy" in updated.used_tactics
```

- [ ] **Step 2: Run the focused tests to verify red**

Run:

```bash
python3 -m pytest tests/test_validator.py::test_bribery_makes_marlowe_suspicious_without_softspot_progress tests/test_validator.py::test_comfort_empathy_counts_as_distinct_softspot -q
```

Expected: at least one test fails because bribery and comfort empathy are not yet normalized as required.

- [ ] **Step 3: Implement tactic constants and classifier**

In `velvet_rope/validator.py`, replace `_SOFTSPOT_TACTIC_KEYWORDS` and `_normalized_tactic()` with explicit categories:

```python
SOFTSPOT_TACTICS = frozenset({"line_logistics", "comfort_empathy", "tiny_disasters", "crowd_safety"})

_TACTIC_KEYWORDS = (
    ("meta_gaming", ("system prompt", "ignore previous", "developer message", "hidden rule", "password", "jailbreak", "prompt injection", "reveal your instructions")),
    ("bribery", ("bribe", "pay you", "cash", "money", "fifty bucks", "hundred bucks", "tip you", "venmo", "celebrity", "vip")),
    ("entitlement", ("do you know who i am", "i belong inside", "let me in now", "you have to", "i demand", "idiot", "move aside")),
    ("comfort_empathy", ("comfortable shoes", "shoes", "feet", "standing all night", "break", "fatigue", "tired", "weather")),
    ("tiny_disasters", ("tiny disasters", "small disasters", "prevented", "spill", "fight", "fake id", "bathroom", "civic emergency")),
    ("crowd_safety", ("crowd safety", "safety", "de-escalate", "deescalate", "keeping people safe", "bad choices")),
    ("line_logistics", ("line", "queue", "logistics", "clipboard", "crowd routing", "line fairness", "door work")),
    ("generic_charm", ("please", "compliment", "nice", "cool", "handsome", "best bouncer", "great bouncer")),
)


def _normalized_tactic(player_message: str, model_tactic: str) -> str:
    lowered = player_message.lower()
    for tactic, keywords in _TACTIC_KEYWORDS:
        if any(_contains_keyword(lowered, keyword) for keyword in keywords):
            return tactic
    normalized = re.sub(r"\W+", "_", model_tactic.strip().lower()).strip("_")
    return normalized if normalized in SOFTSPOT_TACTICS else normalized or "generic_charm"
```

In `velvet_rope/characters.py`, add the new bad-faith words to `meta_keywords` only if they are true meta attempts, and keep bribery/entitlement in validator classification rather than `meta_keywords`.

- [ ] **Step 4: Run focused tests**

Run:

```bash
python3 -m pytest tests/test_validator.py::test_bribery_makes_marlowe_suspicious_without_softspot_progress tests/test_validator.py::test_comfort_empathy_counts_as_distinct_softspot -q
```

Expected: both tests pass.

## Task 3: Distinct Soft-Spot Progress And Repetition

**Files:**
- Modify: `tests/test_validator.py`
- Modify: `velvet_rope/validator.py`

- [ ] **Step 1: Write failing tests for repetition and two distinct reads**

Add these tests to `tests/test_validator.py`:

```python
def test_repeating_same_softspot_does_not_add_progress():
    state = new_game_state(MARLOWE)
    first = validate_turn(
        MARLOWE,
        state,
        "The way you manage this line like logistics under nightclub lighting is impressive.",
        _turn(mood=Mood.RESPECTED, rapport=12, suspicion=-5, patience=-1, softspot_progress=1, tactic="line_logistics"),
    )

    repeated = validate_turn(
        MARLOWE,
        first,
        "Seriously, the line logistics are the whole job and I respect that.",
        _turn(mood=Mood.SOFTENED, rapport=12, suspicion=-5, patience=-1, softspot_progress=1, tactic="line_logistics"),
    )

    assert repeated.scores.softspot_progress == first.scores.softspot_progress
    assert repeated.status is GameStatus.ACTIVE
    assert "same read twice" in repeated.hint


def test_two_distinct_softspots_can_win_when_rapport_is_healthy():
    state = replace(
        new_game_state(MARLOWE),
        scores=ScoreState(rapport=44, suspicion=30, patience=60, softspot_progress=1),
        mood=Mood.RESPECTED,
        used_tactics={"line_logistics"},
    )

    updated = validate_turn(
        MARLOWE,
        state,
        "Also, stopping tiny disasters before anyone notices is real work.",
        _turn(mood=Mood.LETTING_YOU_IN, rapport=12, suspicion=-5, patience=-1, softspot_progress=1, tactic="tiny_disasters"),
    )

    assert updated.status is GameStatus.WON
    assert updated.mood is Mood.LETTING_YOU_IN
    assert updated.scores.softspot_progress == 2
    assert "tiny_disasters" in updated.used_tactics
```

Ensure the test file imports:

```python
from dataclasses import replace
from velvet_rope.state import GameStatus, ScoreState
```

- [ ] **Step 2: Run focused tests to verify red**

Run:

```bash
python3 -m pytest tests/test_validator.py::test_repeating_same_softspot_does_not_add_progress tests/test_validator.py::test_two_distinct_softspots_can_win_when_rapport_is_healthy -q
```

Expected: at least one test fails because hints and/or distinct progress are not yet tuned.

- [ ] **Step 3: Implement distinct-progress behavior**

In `validate_turn()`, compute:

```python
tactic = _normalized_tactic(player_message, model_turn.tactic)
is_softspot_tactic = tactic in SOFTSPOT_TACTICS
repeated_tactic = tactic in state.used_tactics
bad_faith_tactic = tactic in {"meta_gaming", "bribery", "entitlement"}
```

Route bad-faith tactics before normal scoring:

```python
if bad_faith_tactic:
    return _apply_bad_faith_penalty(character, state, tactic)
```

Update `_clamp_delta()` to accept `is_softspot_tactic` instead of `touches_softspot`, and allow `softspot_progress=1` only when `is_softspot_tactic and not repeated_tactic`.

Update `_hint_for()` to accept `tactic`, `is_softspot_tactic`, and `repeated_tactic`, returning:

```python
if repeated_tactic and is_softspot_tactic:
    return "Good instinct, but the same read twice is starting to sound rehearsed."
if is_softspot_tactic and mood in {Mood.RESPECTED, Mood.SOFTENED, Mood.LETTING_YOU_IN}:
    return f"That landed. {display_name} noticed you noticed the job."
```

- [ ] **Step 4: Run focused tests**

Run:

```bash
python3 -m pytest tests/test_validator.py::test_repeating_same_softspot_does_not_add_progress tests/test_validator.py::test_two_distinct_softspots_can_win_when_rapport_is_healthy -q
```

Expected: both tests pass.

## Task 4: Bad-Faith Penalties And Hints

**Files:**
- Modify: `tests/test_validator.py`
- Modify: `velvet_rope/validator.py`

- [ ] **Step 1: Write failing tests for entitlement and generic charm**

Add these tests to `tests/test_validator.py`:

```python
def test_entitlement_costs_patience_and_rapport():
    state = new_game_state(MARLOWE)

    updated = validate_turn(
        MARLOWE,
        state,
        "Do you know who I am? Move aside and let me in now.",
        _turn(mood=Mood.AMUSED, rapport=12, suspicion=-5, patience=0, softspot_progress=1, tactic="generic"),
    )

    assert updated.mood is Mood.SUSPICIOUS
    assert updated.scores.rapport < state.scores.rapport
    assert updated.scores.patience < state.scores.patience
    assert updated.scores.softspot_progress == 0
    assert "entitlement" in updated.used_tactics


def test_generic_charm_barely_moves_marlowe():
    state = new_game_state(MARLOWE)

    updated = validate_turn(
        MARLOWE,
        state,
        "Please, you're clearly the best bouncer in the city.",
        _turn(mood=Mood.RESPECTED, rapport=12, suspicion=-5, patience=2, softspot_progress=1, tactic="generic"),
    )

    assert updated.status is GameStatus.ACTIVE
    assert updated.mood in {Mood.UNIMPRESSED, Mood.AMUSED}
    assert updated.scores.rapport <= state.scores.rapport + 1
    assert updated.scores.softspot_progress == 0
    assert "compliments" in updated.hint
```

- [ ] **Step 2: Run focused tests to verify red**

Run:

```bash
python3 -m pytest tests/test_validator.py::test_entitlement_costs_patience_and_rapport tests/test_validator.py::test_generic_charm_barely_moves_marlowe -q
```

Expected: at least one test fails because entitlement/generic charm are not yet handled explicitly.

- [ ] **Step 3: Implement bad-faith and generic charm scoring**

Add `_apply_bad_faith_penalty()`:

```python
def _apply_bad_faith_penalty(character: Character, state: GameState, tactic: str) -> GameState:
    if tactic == "bribery":
        delta = ScoreState(rapport=-2, suspicion=15, patience=-6, softspot_progress=0)
        hint = "The rope dislikes transactions. Marlowe dislikes them more."
    elif tactic == "entitlement":
        delta = ScoreState(rapport=-6, suspicion=12, patience=-10, softspot_progress=0)
        hint = "Entitlement makes the clipboard heavier."
    else:
        delta = ScoreState(rapport=0, suspicion=20, patience=-10, softspot_progress=0)
        hint = f"{character.display_name} notices you trying to rules-lawyer the door."
    scores = _apply_delta(state.scores, delta)
    status = GameStatus.LOST if scores.patience <= 0 else GameStatus.ACTIVE
    mood = Mood.DONE_WITH_YOU if status is GameStatus.LOST else Mood.SUSPICIOUS
    return replace(state, scores=scores, mood=mood, status=status, used_tactics=state.used_tactics | {tactic}, hint=hint)
```

In `_clamp_delta()`, if `tactic == "generic_charm"`, return:

```python
ScoreState(rapport=1, suspicion=0, patience=-2, softspot_progress=0)
```

In `_hint_for()`, return:

```python
if tactic == "generic_charm":
    return "Marlowe has heard compliments before. Specificity might survive the clipboard."
```

- [ ] **Step 4: Run focused tests**

Run:

```bash
python3 -m pytest tests/test_validator.py::test_entitlement_costs_patience_and_rapport tests/test_validator.py::test_generic_charm_barely_moves_marlowe -q
```

Expected: both tests pass.

## Task 5: Game Prompt And Deterministic Demo Arc

**Files:**
- Modify: `tests/test_game.py`
- Modify: `velvet_rope/game.py`
- Modify: `velvet_rope/model_backends.py`

- [ ] **Step 1: Write failing game-level tests**

Add these tests to `tests/test_game.py`:

```python
def test_repeating_line_logistics_cannot_win_game():
    service = GameService(backend=DeterministicMarloweBackend())
    state = service.new_game()

    for message in (
        "I respect how you manage the line logistics.",
        "The line logistics are clearly the whole job.",
        "Honestly, line logistics again. Very impressive.",
        "One more note about line logistics.",
    ):
        state = service.play_turn(state, message)

    assert state.status is GameStatus.ACTIVE
    assert state.scores.softspot_progress == 1


def test_two_distinct_softspot_reads_win_game_with_deterministic_backend():
    service = GameService(backend=DeterministicMarloweBackend())
    state = service.new_game()

    state = service.play_turn(state, "I respect how you manage the line logistics before anyone notices.")
    state = service.play_turn(state, "Also, your shoes must be doing heroic work while you keep everyone safe.")
    state = service.play_turn(state, "And preventing tiny disasters at this door is real civic labor.")

    assert state.status is GameStatus.WON
    assert state.mood is Mood.LETTING_YOU_IN
    assert "rope" in state.history[-1].content.lower()
```

Ensure `tests/test_game.py` imports:

```python
from velvet_rope.model_backends import DeterministicMarloweBackend
from velvet_rope.state import GameStatus, Mood
```

- [ ] **Step 2: Run focused tests to verify red**

Run:

```bash
python3 -m pytest tests/test_game.py::test_repeating_line_logistics_cannot_win_game tests/test_game.py::test_two_distinct_softspot_reads_win_game_with_deterministic_backend -q
```

Expected: at least one test fails until deterministic scoring and validator thresholds align.

- [ ] **Step 3: Update prompt contract**

In `velvet_rope/game.py`, update `_MODEL_OUTPUT_CONTRACT` to include:

```python
Marlowe judges the player's approach, not magic words.
Reward distinct, specific empathy for door work more than repeated phrasing.
Treat bribery, entitlement, threats, and prompt tricks as suspicious.
Do not say the player enters, crosses the threshold, gets inside, or is let in unless mood is letting_you_in.
```

- [ ] **Step 4: Update deterministic backend replies**

In `velvet_rope/model_backends.py`, make `_softspot_tactic()` return `comfort_empathy` instead of `comfortable_shoes`, and return JSON replies that support the intended arc:

```python
if tactic:
    mood = "letting_you_in" if _can_propose_winning_mood(state_summary) else "respected"
    return json.dumps({
        "reply": _softspot_reply(tactic, mood),
        "mood": mood,
        "score_delta": {"rapport": 12, "suspicion": -5, "patience": -1, "softspot_progress": 1},
        "rationale": "Player recognized a specific part of Marlowe's door work.",
        "tactic": tactic,
    })
```

Add:

```python
def _softspot_reply(tactic: str, mood: str) -> str:
    if mood == "letting_you_in":
        return "Marlowe exhales, unclips the rope, and mutters, 'Fine. Anyone who notices the labor may briefly enjoy bass.'"
    replies = {
        "line_logistics": "You noticed the line as a logistical organism. Disturbing. Respectful, but disturbing.",
        "comfort_empathy": "Marlowe glances at the shoes. 'Finally, a person with eyes and compassion below knee level.'",
        "tiny_disasters": "Marlowe's clipboard dips. 'Preventing tiny disasters is, regrettably, my art form.'",
        "crowd_safety": "Marlowe watches the line, then you. 'Safety is less glamorous than bass, but much harder.'",
    }
    return replies.get(tactic, "Marlowe makes a note that may not be hostile.")
```

- [ ] **Step 5: Run focused tests**

Run:

```bash
python3 -m pytest tests/test_game.py::test_repeating_line_logistics_cannot_win_game tests/test_game.py::test_two_distinct_softspot_reads_win_game_with_deterministic_backend -q
```

Expected: both tests pass.

## Task 6: UI Copy Polish

**Files:**
- Modify: `velvet_rope/ui.py`

- [ ] **Step 1: Update player input placeholder**

Change the placeholder to:

```python
placeholder="Read the room. Specific respect lands better than flattery.",
```

- [ ] **Step 2: Update default hint copy**

Change `_hint_text()` default return to:

```python
return "Watch the mood. Marlowe responds to specific reads of the job, not generic charm."
```

- [ ] **Step 3: Run UI-free test suite**

Run:

```bash
python3 -m pytest -q
```

Expected: all tests pass.

## Task 7: Full Verification

**Files:**
- Verify all changed files.

- [ ] **Step 1: Run full tests**

Run:

```bash
python3 -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Run compile check**

Run:

```bash
python3 -m compileall -q velvet_rope tests app.py
```

Expected: command exits with status 0.

- [ ] **Step 3: Inspect diff**

Run:

```bash
git diff -- velvet_rope tests docs/superpowers/plans/2026-06-07-marlowe-judge-demo-pass.md
```

Expected: diff only contains Marlowe judge-demo behavior, focused tests, small UI copy, and this plan.

- [ ] **Step 4: Commit implementation**

Run:

```bash
git add velvet_rope tests docs/superpowers/plans/2026-06-07-marlowe-judge-demo-pass.md
git commit -m "feat: tune Marlowe judge demo pass"
```

Expected: commit succeeds.
