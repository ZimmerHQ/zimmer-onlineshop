import os
from pathlib import Path

# Resolve absolute DB path from env (DATABASE_URL). If it's sqlite:///./app.db, make it absolute.
def normalize_database_url(url: str) -> str:
    if url.startswith("sqlite:///"):
        path = url.replace("sqlite:///", "", 1)
        p = Path(path)
        if not p.is_absolute():
            # Make absolute relative to the current working directory (backend/)
            abs_path = Path.cwd() / p
            return f"sqlite:///{abs_path.as_posix()}"
    return url

# Get the normalized database URL
def get_database_url() -> str:
    raw_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    normalized_url = normalize_database_url(raw_url)
    print(f"🔗 Using DATABASE_URL = {normalized_url}")
    return normalized_url 