"""
Human-like behavior simulation to avoid bot detection.

This module provides functions to simulate human behavior patterns:
- Variable typing speed
- Random mouse movements
- Natural scrolling behavior
- Random pauses between actions
"""
import random
import time
from typing import Optional


def human_typing(page, selector: str, text: str, min_delay: float = 0.05, max_delay: float = 0.15):
    """
    Simulate human typing with variable speed between characters.

    Args:
        page: Playwright page object
        selector: CSS selector for the input field
        text: Text to type
        min_delay: Minimum delay between characters (seconds)
        max_delay: Maximum delay between characters (seconds)
    """
    # Clear the field first
    page.fill(selector, '')
    time.sleep(random.uniform(0.1, 0.3))

    # Type character by character with random delays
    for char in text:
        page.type(selector, char, delay=random.uniform(min_delay, max_delay))
        # Occasional longer pause (simulating thinking)
        if random.random() < 0.05:  # 5% chance
            time.sleep(random.uniform(0.3, 0.8))


def random_mouse_movement(page):
    """
    Simulate random mouse movement to look natural.

    Args:
        page: Playwright page object
    """
    try:
        # Get viewport dimensions
        viewport = page.viewport_size
        if viewport:
            x = random.randint(100, viewport['width'] - 100)
            y = random.randint(100, viewport['height'] - 100)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.1, 0.3))
    except:
        pass


def natural_scroll(page, direction: str = 'down', amount: int = None):
    """
    Simulate natural scrolling behavior.

    Args:
        page: Playwright page object
        direction: 'up' or 'down'
        amount: Pixels to scroll (random if None)
    """
    if amount is None:
        amount = random.randint(200, 500)

    # Scroll in small increments for natural feel
    steps = random.randint(3, 5)
    step_size = amount // steps

    for _ in range(steps):
        page.mouse.wheel(0, step_size if direction == 'down' else -step_size)
        time.sleep(random.uniform(0.1, 0.2))


def random_pause(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """
    Add a random pause to simulate human thinking/reading time.

    Args:
        min_seconds: Minimum pause duration
        max_seconds: Maximum pause duration
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def human_click(page, selector: str, delay_before: float = 0.3, delay_after: float = 0.5):
    """
    Simulate human click with natural delays.

    Args:
        page: Playwright page object
        selector: CSS selector for the element
        delay_before: Delay before clicking (seconds)
        delay_after: Delay after clicking (seconds)
    """
    # Move mouse to element first
    element = page.locator(selector)
    try:
        element.hover()
        time.sleep(random.uniform(delay_before * 0.5, delay_before * 1.5))
    except:
        pass

    # Click
    element.click()
    time.sleep(random.uniform(delay_after * 0.5, delay_after * 1.5))


def reading_simulation(min_chars: int = 50, max_chars: int = 200):
    """
    Simulate reading time based on text length.

    Assumes average reading speed of 200-300 words per minute.

    Args:
        min_chars: Minimum characters to read
        max_chars: Maximum characters to read
    """
    chars = random.randint(min_chars, max_chars)
    # Reading speed: ~3-5 chars per second
    reading_time = chars / random.uniform(3, 5)
    time.sleep(reading_time)


def random_application_delay():
    """
    Random delay between job applications to avoid detection.

    Returns:
        Delay in seconds (between 10-60 seconds)
    """
    return random.uniform(10, 60)


def enhanced_page_navigation(page, url: str):
    """
    Navigate to a page with human-like behavior.

    Args:
        page: Playwright page object
        url: URL to navigate to
    """
    # Navigate
    page.goto(url)

    # Wait for load with random delay
    time.sleep(random.uniform(1.5, 3.0))

    # Random scroll to simulate exploring
    if random.random() < 0.3:  # 30% chance
        natural_scroll(page, 'down', random.randint(100, 300))
        time.sleep(random.uniform(0.5, 1.0))


def setup_human_like_context(context, page=None):
    """
    Configure browser context with human-like settings.

    Args:
        context: Playwright browser context
        page: Playwright page (optional, for viewport size)
    """
    # Set realistic viewport on page if provided
    if page:
        page.set_viewport_size(random.choice([
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1440, 'height': 900},
        ]))

    # Set realistic user agent
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    context.set_extra_http_headers({
        'User-Agent': random.choice(user_agents),
        'Accept-Language': 'en-US,en;q=0.9',
    })
