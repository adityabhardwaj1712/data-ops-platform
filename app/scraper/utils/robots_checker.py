class RobotsChecker:
    async def is_allowed(self, url: str, user_agent: str = "*") -> bool:
        return True


robots_checker = RobotsChecker()

