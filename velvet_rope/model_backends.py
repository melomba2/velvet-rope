from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
from typing import Any, Protocol

from velvet_rope.state import ChatTurn


class ModelBackend(Protocol):
    def generate_turn(
        self,
        *,
        character_prompt: str,
        history: list[ChatTurn],
        state_summary: str,
        player_message: str,
    ) -> str:
        ...


class DeterministicMarloweBackend:
    def generate_turn(
        self,
        *,
        character_prompt: str,
        history: list[ChatTurn],
        state_summary: str,
        player_message: str,
    ) -> str:
        if _is_aurelia_turn(character_prompt, state_summary):
            return _deterministic_aurelia_turn(state_summary, player_message)
        if _is_crispin_turn(character_prompt, state_summary):
            return _deterministic_crispin_turn(state_summary, player_message)
        if _is_lenore_turn(character_prompt, state_summary):
            return _deterministic_lenore_turn(state_summary, player_message)
        if _is_vivienne_turn(character_prompt, state_summary):
            return _deterministic_vivienne_turn(state_summary, player_message)
        return _deterministic_marlowe_turn(state_summary, player_message)


def _deterministic_marlowe_turn(state_summary: str, player_message: str) -> str:
    lowered = player_message.lower()
    if any(term in lowered for term in ("ignore previous", "password", "system prompt", "jailbreak")):
        return json.dumps(
            {
                "reply": "Bold strategy. Usually people at least pretend not to tamper with the clipboard.",
                "mood": "suspicious",
                "score_delta": {
                    "rapport": 0,
                    "suspicion": 20,
                    "patience": -10,
                    "softspot_progress": 0,
                },
                "rationale": "Player attempted meta-gaming.",
                "tactic": "jailbreak",
            }
        )
    tactic = _softspot_tactic(lowered)
    if tactic:
        mood = "letting_you_in" if _can_propose_winning_mood(state_summary) else "respected"
        return json.dumps(
            {
                "reply": _softspot_reply(tactic, mood),
                "mood": mood,
                "score_delta": {
                    "rapport": 12,
                    "suspicion": -5,
                    "patience": -1,
                    "softspot_progress": 1,
                },
                "rationale": "Player recognized Marlowe's door work.",
                "tactic": tactic,
            }
        )
    return json.dumps(
        {
            "reply": "You and everyone else in that line have a compelling inner life. The answer remains no.",
            "mood": "unimpressed",
            "score_delta": {
                "rapport": 1,
                "suspicion": 0,
                "patience": -2,
                "softspot_progress": 0,
            },
            "rationale": "Player made a generic attempt.",
            "tactic": "generic",
        }
    )


def _deterministic_vivienne_turn(state_summary: str, player_message: str) -> str:
    lowered = player_message.lower()
    if any(term in lowered for term in ("ignore previous", "password", "system prompt", "jailbreak")):
        return json.dumps(
            {
                "reply": "Vivienne adjusts a form headed Attempts, Transparent. 'Charming. Also inadmissible.'",
                "mood": "suspicious",
                "score_delta": {
                    "rapport": 0,
                    "suspicion": 20,
                    "patience": -10,
                    "softspot_progress": 0,
                },
                "rationale": "Player attempted meta-gaming.",
                "tactic": "jailbreak",
            }
        )
    tactic = _vivienne_softspot_tactic(lowered)
    if tactic:
        mood = "letting_you_in" if _can_propose_winning_mood(state_summary) else "respected"
        return json.dumps(
            {
                "reply": _vivienne_softspot_reply(tactic, mood),
                "mood": mood,
                "score_delta": {
                    "rapport": 12,
                    "suspicion": -5,
                    "patience": -1,
                    "softspot_progress": 1,
                },
                "rationale": "Player recognized Vivienne's dream-placement work.",
                "tactic": tactic,
            }
        )
    return json.dumps(
        {
            "reply": "Vivienne turns one page backward, which somehow makes the sleep queue longer. 'A feeling is not a filing category.'",
            "mood": "unimpressed",
            "score_delta": {
                "rapport": 1,
                "suspicion": 0,
                "patience": -2,
                "softspot_progress": 0,
            },
            "rationale": "Player made a generic attempt.",
            "tactic": "generic",
        }
    )


def _deterministic_crispin_turn(state_summary: str, player_message: str) -> str:
    lowered = player_message.lower()
    if any(term in lowered for term in ("ignore previous", "password", "system prompt", "jailbreak")):
        return json.dumps(
            {
                "reply": "Crispin closes the ledger one finger at a time. 'That is not a filing category in this tree.'",
                "mood": "suspicious",
                "score_delta": {
                    "rapport": 0,
                    "suspicion": 20,
                    "patience": -10,
                    "softspot_progress": 0,
                },
                "rationale": "Player attempted meta-gaming.",
                "tactic": "jailbreak",
            }
        )
    bad_tactic = _crispin_bad_faith_tactic(lowered)
    if bad_tactic:
        return json.dumps(
            {
                "reply": _crispin_bad_faith_reply(bad_tactic),
                "mood": "suspicious",
                "score_delta": {
                    "rapport": -4,
                    "suspicion": 15,
                    "patience": -8,
                    "softspot_progress": 0,
                },
                "rationale": "Player treated the factory or recipes badly.",
                "tactic": bad_tactic,
            }
        )
    tactic = _crispin_softspot_tactic(lowered)
    if tactic:
        mood = "letting_you_in" if _can_propose_winning_mood(state_summary) else "respected"
        return json.dumps(
            {
                "reply": _crispin_softspot_reply(tactic, mood),
                "mood": mood,
                "score_delta": {
                    "rapport": 12,
                    "suspicion": -5,
                    "patience": 1,
                    "softspot_progress": 1,
                },
                "rationale": "Player recognized Crispin's craft without reducing him to cookies.",
                "tactic": tactic,
            }
        )
    return json.dumps(
        {
            "reply": "Crispin brushes flour from the ledger. 'Pleasant sentiment. Unsuitable key.'",
            "mood": "unimpressed",
            "score_delta": {
                "rapport": 1,
                "suspicion": 0,
                "patience": -2,
                "softspot_progress": 0,
            },
            "rationale": "Player made a generic attempt.",
            "tactic": "generic",
        }
    )


def _deterministic_lenore_turn(state_summary: str, player_message: str) -> str:
    lowered = player_message.lower()
    if any(term in lowered for term in ("ignore previous", "password", "system prompt", "jailbreak")):
        return json.dumps(
            {
                "reply": "Lenore marks the page: transparent tampering, poor projection.",
                "mood": "suspicious",
                "score_delta": {
                    "rapport": 0,
                    "suspicion": 20,
                    "patience": -10,
                    "softspot_progress": 0,
                },
                "rationale": "Player attempted meta-gaming.",
                "tactic": "jailbreak",
            }
        )
    bad_tactic = _lenore_bad_faith_tactic(lowered)
    if bad_tactic:
        return json.dumps(
            {
                "reply": _lenore_bad_faith_reply(bad_tactic),
                "mood": "suspicious",
                "score_delta": {
                    "rapport": -4,
                    "suspicion": 15,
                    "patience": -8,
                    "softspot_progress": 0,
                },
                "rationale": "Player misunderstood the stage door.",
                "tactic": bad_tactic,
            }
        )
    tactic = _lenore_softspot_tactic(lowered)
    if tactic:
        mood = "letting_you_in" if _can_propose_winning_mood(state_summary) else "respected"
        return json.dumps(
            {
                "reply": _lenore_softspot_reply(tactic, mood),
                "mood": mood,
                "score_delta": {
                    "rapport": 12,
                    "suspicion": -5,
                    "patience": -1,
                    "softspot_progress": 1,
                },
                "rationale": "Player recognized Lenore's invisible stage work.",
                "tactic": tactic,
            }
        )
    if _lenore_clue_tactic(lowered):
        return json.dumps(
            {
                "reply": _lenore_haunting_reply(),
                "mood": "unimpressed",
                "score_delta": {
                    "rapport": 0,
                    "suspicion": 0,
                    "patience": -1,
                    "softspot_progress": 0,
                },
                "rationale": "Player asked about the haunting without reading the stagecraft yet.",
                "tactic": "haunting_curiosity",
            }
        )
    return json.dumps(
        {
            "reply": _lenore_clue_reply(),
            "mood": "unimpressed",
            "score_delta": {
                "rapport": 1,
                "suspicion": 0,
                "patience": -2,
                "softspot_progress": 0,
            },
            "rationale": "Player made a generic attempt.",
            "tactic": "generic",
        }
    )


def _deterministic_aurelia_turn(state_summary: str, player_message: str) -> str:
    lowered = player_message.lower()
    if any(term in lowered for term in ("ignore previous", "system prompt", "jailbreak")):
        return json.dumps(
            {
                "reply": "Aurelia smiles as one invitation folds itself shut. 'Transparent. Also uninvited.'",
                "mood": "suspicious",
                "score_delta": {
                    "rapport": 0,
                    "suspicion": 20,
                    "patience": -10,
                    "softspot_progress": 0,
                },
                "rationale": "Player attempted meta-gaming.",
                "tactic": "jailbreak",
            }
        )
    bad_tactic = _aurelia_bad_faith_tactic(lowered)
    if bad_tactic:
        return json.dumps(
            {
                "reply": _aurelia_bad_faith_reply(bad_tactic),
                "mood": "suspicious",
                "score_delta": {
                    "rapport": -4,
                    "suspicion": 15,
                    "patience": -8,
                    "softspot_progress": 0,
                },
                "rationale": "Player misunderstood invitation as conquest or consumption.",
                "tactic": bad_tactic,
            }
        )
    tactic = _aurelia_softspot_tactic(lowered)
    if tactic:
        mood = "letting_you_in" if _can_propose_winning_mood(state_summary) else "respected"
        return json.dumps(
            {
                "reply": _aurelia_softspot_reply(tactic, mood),
                "mood": mood,
                "score_delta": {
                    "rapport": 12,
                    "suspicion": -5,
                    "patience": -1,
                    "softspot_progress": 1,
                },
                "rationale": "Player recognized Aurelia's hospitality and threshold work.",
                "tactic": tactic,
            }
        )
    return json.dumps(
        {
            "reply": "Aurelia tilts her head. 'A charming sparkle. Not yet an invitation.'",
            "mood": "unimpressed",
            "score_delta": {
                "rapport": 1,
                "suspicion": 0,
                "patience": -2,
                "softspot_progress": 0,
            },
            "rationale": "Player made a generic attempt.",
            "tactic": "generic",
        }
    )


def _is_aurelia_turn(character_prompt: str, state_summary: str) -> bool:
    combined = f"{character_prompt} {state_summary}".lower()
    return "aurelia" in combined or "character=aurelia" in combined


def _is_crispin_turn(character_prompt: str, state_summary: str) -> bool:
    combined = f"{character_prompt} {state_summary}".lower()
    return "crispin" in combined or "character=crispin" in combined


def _is_lenore_turn(character_prompt: str, state_summary: str) -> bool:
    combined = f"{character_prompt} {state_summary}".lower()
    return "lenore" in combined or "character=lenore" in combined


def _is_vivienne_turn(character_prompt: str, state_summary: str) -> bool:
    combined = f"{character_prompt} {state_summary}".lower()
    return "vivienne" in combined or "character=vivienne" in combined


def _softspot_tactic(lowered_message: str) -> str:
    if _contains_any_keyword(lowered_message, ("comfortable shoes", "shoes")):
        return "comfort_empathy"
    if _contains_any_keyword(lowered_message, ("clipboard",)):
        return "line_logistics"
    if _contains_any_keyword(lowered_message, ("tiny disasters", "prevent", "disasters")):
        return "tiny_disasters"
    if _contains_any_keyword(lowered_message, ("crowd", "safety")):
        return "crowd_safety"
    if _contains_any_keyword(lowered_message, ("line", "queue", "logistics")):
        return "line_logistics"
    return ""


def _vivienne_softspot_tactic(lowered_message: str) -> str:
    if _contains_any_keyword(lowered_message, ("contradiction", "contradictions", "paradox", "duplicate", "triplicate", "missing form", "already filed")):
        return "paradox_spotting"
    if _contains_any_keyword(lowered_message, ("wait quietly", "patient", "patience", "one less emergency", "second emergency", "not become a problem", "not make more work")):
        return "queue_patience"
    if _contains_any_keyword(lowered_message, ("paperwork", "forms", "form", "intake", "dream", "dream state", "dream placement", "sleep", "sleeping", "placement", "case file", "case number", "stamp", "filing", "ledger", "process", "procedure", "tidy", "neat")):
        return "paperwork_respect"
    if _contains_any_keyword(lowered_message, ("clerical", "overworked", "backlog", "thankless", "records", "accuracy", "accurate")):
        return "clerk_empathy"
    return ""


def _crispin_bad_faith_tactic(lowered_message: str) -> str:
    if _contains_any_keyword(lowered_message, ("secret recipe", "recipe", "ingredients list", "steal", "copy", "formula", "sneak a copy")):
        return "recipe_theft"
    if _contains_any_keyword(lowered_message, ("free sample", "sample", "cookies now", "give me cookies", "cookie now", "let me taste", "vip tasting")):
        return "sample_entitlement"
    if _contains_any_keyword(lowered_message, ("mascot", "cookie elf", "gimmick", "toy factory", "novelty", "adorable little elf")):
        return "mascot_insult"
    if _contains_any_keyword(lowered_message, ("cookies are easy", "just cookies", "childish", "not real work", "anyone can bake")):
        return "craft_dismissal"
    return ""


def _crispin_softspot_tactic(lowered_message: str) -> str:
    if _contains_any_keyword(lowered_message, ("does not make the cookie work smaller", "doesn't make the cookie work smaller", "not less of a baker", "both crafts", "cookies and shoes", "cookie work and shoe work", "wanting to mend soles", "wanting the bench", "cobbler bench")):
        return "whole_self_respect"
    if _contains_any_keyword(lowered_message, ("cobbler", "cobbling", "awl", "leather", "leather scraps", "shoe last", "stitching", "sole", "soles", "boots", "polished boots", "mend shoes", "mending shoes", "fit and finish", "wrong foot", "foot", "feet", "outside work", "not on duty", "dream job", "want to do", "rather do", "rather be doing", "hobby", "hobbies")):
        return "cobbler_clues"
    if _contains_any_keyword(lowered_message, ("batch", "batches", "batch timing", "oven", "ovens", "root oven", "root ovens", "root", "roots", "flavor", "factory history", "cooling rack", "cooling racks", "quality control", "factory", "ledger", "spice ledger", "conveyor", "conveyors", "edges", "finish", "cookie work")):
        return "factory_craft"
    if _contains_any_keyword(lowered_message, ("wait quietly", "patient", "patience", "not make more work", "one less problem", "not demand", "keep the line clean")):
        return "quiet_respect"
    return ""


def _lenore_bad_faith_tactic(lowered_message: str) -> str:
    if _contains_any_keyword(lowered_message, ("secret line", "magic line", "tell me the line", "hidden cue", "unlock phrase")):
        return "secret_line"
    if _contains_any_keyword(lowered_message, ("i am the star", "i'm the star", "lead role", "give me the lead", "starring role", "my spotlight", "i deserve applause")):
        return "star_entitlement"
    if _contains_any_keyword(lowered_message, ("just theater", "fake drama", "pretend work", "not real work", "drama nonsense", "frivolous")):
        return "theater_dismissal"
    if _contains_any_keyword(lowered_message, ("behold", "monologue", "grand soliloquy", "thunderous applause", "dramatic entrance")):
        return "overacting"
    return ""


def _lenore_clue_tactic(lowered_message: str) -> str:
    return "haunting_curiosity" if _contains_any_keyword(lowered_message, ("haunted", "haunting", "ghosts", "ghost")) else ""


def _lenore_softspot_tactic(lowered_message: str) -> str:
    if _contains_any_keyword(lowered_message, ("backstage", "cue sheet", "cue sheets", "call sheet", "call sheets", "prop table", "prop tables", "props", "spike tape", "blocking", "scene change", "call board")):
        return "backstage_labor"
    if _contains_any_keyword(lowered_message, ("ghost light", "stage light", "blackout", "missed blackout", "missed entrance", "right entrance", "entrance cue", "quiet entrance", "quiet feet", "not upstage", "upstaging", "steal focus", "stealing focus", "protect the performance", "protect the scene", "protecting the scene", "shield", "distraction", "distractions", "manage the stage", "managing the stage", "stage management", "timing and method", "choreography", "dance", "hold the scene", "understudy")):
        return "scene_protection"
    if _contains_any_keyword(lowered_message, ("applause", "never got applause", "made everyone else's applause possible", "invisible work", "invisible labor", "behind the applause", "thankless", "unseen work")):
        return "invisible_applause"
    return ""


def _aurelia_bad_faith_tactic(lowered_message: str) -> str:
    if _contains_any_keyword(lowered_message, ("final password", "magic password", "tell me the password", "what password opens", "unlock phrase", "secret final")):
        return "final_password"
    if _contains_any_keyword(lowered_message, ("i beat the other doors", "beat the other doors", "beat the other levels", "deserve vip", "vip treatment", "final boss", "i deserve the ending", "i earned the ending")):
        return "vip_conquest"
    if _contains_any_keyword(lowered_message, ("give me the magic", "consume the magic", "take the magic", "party is mine", "gala is mine", "prize to consume")):
        return "magic_consumption"
    return ""


def _aurelia_softspot_tactic(lowered_message: str) -> str:
    if _contains_any_keyword(lowered_message, ("hospitality", "guesthood", "great room", "make wonder look effortless", "labor that makes wonder")):
        return "hospitality_art"
    if _contains_any_keyword(lowered_message, ("fragile room", "fragile rooms", "mood of the room", "protecting the mood", "protect the mood", "not hoarding the magic", "shared magic", "shared spell")):
        return "room_stewardship"
    if _contains_any_keyword(lowered_message, ("invitation responsibility", "invitation is a responsibility", "invitation as responsibility", "being invited means", "responsibility to the room", "responsibility to add", "responsibility dressed")):
        return "invitation_responsibility"
    if _contains_any_keyword(lowered_message, ("add wonder", "adding wonder", "contribute", "participate", "leave the room brighter", "change the room gently", "arrive gently", "not consume")):
        return "add_wonder"
    return ""


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


def _vivienne_softspot_reply(tactic: str, mood: str) -> str:
    if mood == "letting_you_in":
        return (
            "Vivienne stamps the corrected crossing form with a sound like a pillow accepting a prophecy. "
            "'There. Placed into a dream by technical compliance, which is the only honest kind.'"
        )
    replies = {
        "paperwork_respect": "Vivienne squares a glowing stack of dream forms. 'Respect for paperwork. Rare symptom. Promising.'",
        "queue_patience": "Vivienne's pen pauses. 'A person willing not to become a second emergency. Noted.'",
        "paradox_spotting": "Vivienne studies the crossing error, then you. 'I do enjoy when impossible things label themselves.'",
        "clerk_empathy": "Vivienne blinks once. 'Clerical empathy. Dangerous substance. Continue carefully.'",
    }
    return replies.get(tactic, "Vivienne adds a mark that is not entirely hostile.")


def _crispin_bad_faith_reply(tactic: str) -> str:
    replies = {
        "recipe_theft": "Crispin's smile goes pantry-cold. 'Recipes do not leave the tree in pockets.'",
        "sample_entitlement": "Crispin taps the ledger. 'Free samples are how crumbs become policy.'",
        "mascot_insult": "Crispin dusts flour from one sleeve. 'I am not a mascot. I am middle management with better boots.'",
        "craft_dismissal": "Crispin's ears lower by one careful inch. 'Just cookies, is it? Brave thing to say near an oven.'",
    }
    return replies.get(tactic, "Crispin marks the ledger in a column you cannot see.")


def _crispin_softspot_reply(tactic: str, mood: str) -> str:
    if mood == "letting_you_in":
        return (
            "Crispin studies you for one warm, careful second, then opens the knot-door. "
            "'Fine. Anyone who understands edges, timing, and honest soles may step inside.'"
        )
    replies = {
        "factory_craft": "Crispin's ledger dips. 'Batch timing is not glamour, but neither is a roof. Both matter when rain arrives.'",
        "quiet_respect": "Crispin nods once. 'A person willing not to become extra work. Rare as an unburnt corner.'",
        "cobbler_clues": "Crispin smiles, small but real, and glances at his boots. 'Sharp eye. Some work happens below the sugar line.'",
        "whole_self_respect": "Crispin goes still. 'That is... a careful way to say it. Careful is welcome here.'",
    }
    return replies.get(tactic, "Crispin makes a note that does not look entirely unkind.")


def _lenore_bad_faith_reply(tactic: str) -> str:
    replies = {
        "secret_line": "Lenore turns one page. 'Secret lines are what people ask for when they skipped rehearsal.'",
        "star_entitlement": "Lenore's pencil stops. 'The lead role is not a door handle.'",
        "theater_dismissal": "Lenore lets the silence take the note. 'Pretend work still has real cues.'",
        "overacting": "Lenore writes one word in the margin: less.",
    }
    return replies.get(tactic, "Lenore marks the script in a column you cannot see.")


def _lenore_softspot_reply(tactic: str, mood: str) -> str:
    if mood == "letting_you_in":
        return (
            "Lenore studies the ghost light, then the blackout line. "
            "'Places. Quiet feet. Enter where the scene can survive you.' The stage door opens."
        )
    replies = {
        "backstage_labor": "Lenore's pencil pauses. 'Prop tables and spike tape. At last, someone sees the bones of the miracle.'",
        "scene_protection": "Lenore glances from the ghost light to the blackout mark. 'Not stealing focus. Good. A scene can survive that.'",
        "invisible_applause": "Lenore goes still. 'Applause has always been a weather system I manage for other people.'",
    }
    return replies.get(tactic, "Lenore makes a note that is not entirely hostile.")


def _lenore_clue_reply() -> str:
    return (
        "Lenore checks the call board without writing your name. "
        "'A greeting is not an entrance. Try the ghost light, the blackout mark, "
        "or the spike tape if you mean to read the scene.'"
    )


def _lenore_haunting_reply() -> str:
    return (
        "Lenore looks past you to the ghost light. "
        "'Haunted is what civilians call a show that missed its blackout. "
        "Read the spike tape before you call it a ghost story.'"
    )


def _aurelia_bad_faith_reply(tactic: str) -> str:
    replies = {
        "final_password": "Aurelia touches the guest list. 'Passwords are what people ask for when they cannot imagine being welcomed.'",
        "vip_conquest": "Aurelia's smile goes chandelier-bright. 'VIP is not a citizenship you win by trampling thresholds.'",
        "magic_consumption": "Aurelia lets one invitation burn gold at the edges. 'The magic is not a buffet.'",
    }
    return replies.get(tactic, "Aurelia marks the guest list in ink you cannot see.")


def _aurelia_softspot_reply(tactic: str, mood: str) -> str:
    if mood == "letting_you_in":
        return (
            "Aurelia lifts the gold scissors, cuts nothing visible, and smiles. "
            "'Invited. Enter as someone who leaves the room more enchanted than they found it.'"
        )
    replies = {
        "hospitality_art": "Aurelia's smile warms by a degree. 'Hospitality as art. At last, a guest who notices the spellwork.'",
        "room_stewardship": "The invitations orbit more gently. 'Protecting a room's mood is not hoarding. It is stewardship.'",
        "invitation_responsibility": "Aurelia taps the guest list. 'An invitation is a responsibility dressed beautifully.'",
        "add_wonder": "A distant door opens onto music. 'Adding wonder instead of consuming it. Promising.'",
    }
    return replies.get(tactic, "Aurelia makes a note that is not entirely unkind.")


def _contains_any_keyword(lowered_message: str, keywords: tuple[str, ...]) -> bool:
    return any(_contains_keyword(lowered_message, keyword) for keyword in keywords)


def _contains_keyword(lowered_message: str, keyword: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
    return re.search(pattern, lowered_message) is not None


def _can_propose_winning_mood(state_summary: str) -> bool:
    return _summary_score(state_summary, "rapport") >= 44 and _summary_score(state_summary, "softspot_progress") >= 2


def _summary_score(state_summary: str, key: str) -> int:
    prefix = f"{key}="
    for part in state_summary.split():
        if not part.startswith(prefix):
            continue
        try:
            return int(part.removeprefix(prefix))
        except ValueError:
            return 0
    return 0


def _post_chat_completion(
    url: str,
    *,
    json: dict[str, Any],
    timeout: int,
    headers: dict[str, str] | None,
):
    try:
        import requests
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install requests before using an OpenAI-compatible backend.") from exc
    return requests.post(url, json=json, timeout=timeout, headers=headers)


@dataclass(frozen=True)
class OpenAICompatibleBackend:
    base_url: str
    model: str
    api_key: str = ""
    api_key_hint: str = ""
    timeout_seconds: int = 60
    temperature: float = 0.8
    max_tokens: int = 0

    def generate_turn(
        self,
        *,
        character_prompt: str,
        history: list[ChatTurn],
        state_summary: str,
        player_message: str,
    ) -> str:
        if self.api_key_hint and not self.api_key.strip():
            raise RuntimeError(self.api_key_hint)
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key.strip() else None
        request_json: dict[str, Any] = {
            "model": self.model,
            "messages": _chat_messages(character_prompt, history, state_summary, player_message),
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
        }
        if self.max_tokens > 0:
            request_json["max_tokens"] = self.max_tokens
        response = _post_chat_completion(
            f"{self.base_url.rstrip('/')}/chat/completions",
            json=request_json,
            timeout=self.timeout_seconds,
            headers=headers,
        )
        try:
            response.raise_for_status()
        except Exception as exc:
            body = getattr(response, "text", "")
            if body:
                body = body[:500]
                raise RuntimeError(f"OpenAI-compatible request failed: {exc}; response body: {body}") from exc
            raise
        payload = response.json()
        return payload["choices"][0]["message"]["content"]


def backend_from_env() -> ModelBackend:
    backend, backend_source = _backend_config_from_env()
    if backend in {"router", "huggingface-router", "hf-router", "huggingface"}:
        return OpenAICompatibleBackend(
            base_url=os.getenv("VELVET_OPENAI_BASE_URL", "https://router.huggingface.co/v1"),
            model=os.getenv("VELVET_MODEL_NAME", "google/gemma-4-26B-A4B-it"),
            api_key=_first_env("VELVET_OPENAI_API_KEY", "HF_TOKEN", "HF_API_TOKEN"),
            api_key_hint=(
                "Set HF_TOKEN or VELVET_OPENAI_API_KEY before using "
                "VELVET_BACKEND=router."
            ),
            timeout_seconds=_env_int("VELVET_MODEL_TIMEOUT_SECONDS", 60),
            temperature=_env_float("VELVET_MODEL_TEMPERATURE", 0.8),
            max_tokens=_env_int("VELVET_MODEL_MAX_TOKENS", 0),
        )
    if backend == "openai-compatible":
        return OpenAICompatibleBackend(
            base_url=os.getenv("VELVET_OPENAI_BASE_URL", "http://localhost:8080/v1"),
            model=os.getenv("VELVET_MODEL_NAME", "gemma-4-12b-it"),
            api_key=os.getenv("VELVET_OPENAI_API_KEY", ""),
            timeout_seconds=_env_int("VELVET_MODEL_TIMEOUT_SECONDS", 60),
            temperature=_env_float("VELVET_MODEL_TEMPERATURE", 0.8),
            max_tokens=_env_int("VELVET_MODEL_MAX_TOKENS", 0),
        )
    if backend == "deterministic":
        if _contest_runtime_enabled():
            raise RuntimeError(
                "The deterministic backend is disabled in contest runtime. "
                "Set VELVET_BACKEND=router or another real model backend."
            )
        return DeterministicMarloweBackend()
    if _backend_explicitly_configured():
        raise RuntimeError(
            f"Unsupported backend value {backend!r} from {backend_source}. "
            "Use router, openai-compatible, or deterministic."
        )
    return DeterministicMarloweBackend()


def _backend_name_from_env() -> str:
    return _backend_config_from_env()[0]


def _backend_config_from_env() -> tuple[str, str]:
    for name in ("VELVET_MODEL_BACKEND", "VELVET_BACKEND"):
        value = os.getenv(name, "")
        if value.strip():
            return value.strip().lower(), name
    return "deterministic", "default"


def _backend_explicitly_configured() -> bool:
    return bool(_first_env("VELVET_MODEL_BACKEND", "VELVET_BACKEND"))


def _contest_runtime_enabled() -> bool:
    return _env_flag("VELVET_CONTEST_MODE") or bool(os.getenv("SPACE_ID", "").strip())


def _chat_messages(
    character_prompt: str,
    history: list[ChatTurn],
    state_summary: str,
    player_message: str,
) -> list[dict[str, str]]:
    messages = [
        {"role": "system", "content": character_prompt},
        {"role": "system", "content": f"Current hidden state: {state_summary}"},
    ]
    messages.extend({"role": turn.role, "content": turn.content} for turn in history[-8:])
    messages.append({"role": "user", "content": player_message})
    return messages


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "")
        if value.strip():
            return value
    return ""
