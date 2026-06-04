import os

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
WELCOME_NAME = os.environ.get("WELCOME_NAME", "💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 𝑶𝑷 𝑩𝒐𝒕 💗")
REPO_URL = os.environ.get("REPO_URL", "")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "@replyraid")
SONG_PATH = os.environ.get("SONG_PATH", "songs/song.mp3")
