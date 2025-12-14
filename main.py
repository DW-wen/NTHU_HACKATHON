import os
import sys
from src.core.engine import Engine
from src.utils import GameSettings, Logger


def _configure_online():
    # Enable online via env var ONLINE=1 or --online flag
    if os.environ.get("ONLINE", "0") == "1" or "--online" in sys.argv:
        GameSettings.IS_ONLINE = True
        Logger.info("Online mode enabled")
    # Allow overriding server URL
    for i, a in enumerate(sys.argv):
        if a == "--server" and i + 1 < len(sys.argv):
            GameSettings.ONLINE_SERVER_URL = sys.argv[i + 1]
            Logger.info(f"Online server URL set to {GameSettings.ONLINE_SERVER_URL}")


if __name__ == "__main__":
    _configure_online()
    engine = Engine()
    engine.run()

