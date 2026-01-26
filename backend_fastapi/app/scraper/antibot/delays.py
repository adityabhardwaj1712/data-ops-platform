"""
Human-like Delays and Mouse Movements
Simulates realistic human interaction patterns
"""
import asyncio
import random
from typing import Optional


async def human_like_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
    """
    Wait a random amount of time to simulate human behavior.
    
    Args:
        min_seconds: Minimum delay
        max_seconds: Maximum delay
    """
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


async def typing_delay():
    """Simulate delay between keystrokes"""
    await asyncio.sleep(random.uniform(0.05, 0.15))


async def random_mouse_move(page, moves: int = 3):
    """
    Perform random mouse movements on a page.
    
    Args:
        page: Playwright page object
        moves: Number of movements to make
    """
    try:
        viewport = page.viewport_size
        if not viewport:
            return
        
        for _ in range(moves):
            x = random.randint(100, viewport["width"] - 100)
            y = random.randint(100, viewport["height"] - 100)
            
            # Move mouse with slight randomization
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            await asyncio.sleep(random.uniform(0.1, 0.3))
    except Exception:
        # Ignore mouse movement errors
        pass


async def random_scroll(page, direction: str = "down"):
    """
    Perform a random scroll action.
    
    Args:
        page: Playwright page object
        direction: "up" or "down"
    """
    try:
        scroll_amount = random.randint(100, 500)
        if direction == "up":
            scroll_amount = -scroll_amount
        
        await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        await human_like_delay(0.2, 0.5)
    except Exception:
        pass


def get_random_delay_pattern() -> list:
    """
    Get a random pattern of delays to use between actions.
    Returns a list of delay values.
    """
    patterns = [
        [0.5, 1.0, 0.3, 0.8],  # Quick reader
        [1.0, 2.0, 1.5, 1.0],  # Normal reader
        [2.0, 3.0, 2.5, 1.5],  # Slow reader
        [0.8, 1.2, 0.5, 2.0],  # Variable reader
    ]
    return random.choice(patterns)
