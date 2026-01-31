import asyncio
import random
from playwright.async_api import Page

async def human_like_delay(min_ms: int = 500, max_ms: int = 2500):
    """
    Simulates a human-like pause.
    """
    delay = random.randint(min_ms, max_ms) / 1000.0
    await asyncio.sleep(delay)

async def random_mouse_move(page: Page):
    """
    Simulates random mouse movements on the page.
    """
    try:
        width = page.viewport_size["width"] if page.viewport_size else 1280
        height = page.viewport_size["height"] if page.viewport_size else 800
        
        # Move to a few random points
        for _ in range(random.randint(2, 5)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            await asyncio.sleep(random.uniform(0.1, 0.5))
    except Exception:
        pass # Don't let bot-masking fail the scrape
