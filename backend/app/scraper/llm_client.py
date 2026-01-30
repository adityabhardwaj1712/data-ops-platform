class LLMClient:
    def __init__(self, provider: str | None = None):
        self.provider = provider or "noop"

    def extract(self, text: str) -> dict:
        # Placeholder for future LLM extraction
        return {}
