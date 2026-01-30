import random

USER_AGENTS = [
    "Mozilla/5.0",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X)",
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS)
    }
