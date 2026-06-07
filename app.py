from velvet_rope.game import GameService
from velvet_rope.transcripts import transcript_recorder_from_env
from velvet_rope.ui import build_app


app = build_app(GameService(transcript_recorder=transcript_recorder_from_env()))


if __name__ == "__main__":
    app.launch()
