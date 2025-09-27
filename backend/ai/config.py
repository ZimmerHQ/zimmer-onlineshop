import os
DEBUG_INTENTS = os.getenv("DEBUG_INTENTS", "0") in ("1", "true", "True", "YES", "yes")
