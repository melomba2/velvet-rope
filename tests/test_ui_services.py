from velvet_rope.characters import PLAYABLE_CHARACTERS
from velvet_rope.game import GameService
from velvet_rope.model_backends import DeterministicMarloweBackend, OpenAICompatibleBackend
from velvet_rope.ui import _services_for_levels


def test_services_for_levels_resolves_model_template_per_character():
    backend = OpenAICompatibleBackend(
        base_url="https://example.test/v1",
        model="velvet-{character_id}",
    )
    service = GameService(backend=backend)

    services = _services_for_levels(service)

    assert {
        character.character_id: services[character.character_id].backend.model
        for character in PLAYABLE_CHARACTERS
    } == {
        character.character_id: f"velvet-{character.character_id}"
        for character in PLAYABLE_CHARACTERS
    }


def test_services_for_levels_leaves_constant_model_shared():
    backend = OpenAICompatibleBackend(
        base_url="https://example.test/v1",
        model="gemma-4-12b-it",
    )
    service = GameService(backend=backend)

    services = _services_for_levels(service)

    assert {id(level_service.backend) for level_service in services.values()} == {id(backend)}


def test_services_for_levels_leaves_non_model_backend_shared():
    backend = DeterministicMarloweBackend()
    service = GameService(backend=backend)

    services = _services_for_levels(service)

    assert {id(level_service.backend) for level_service in services.values()} == {id(backend)}
