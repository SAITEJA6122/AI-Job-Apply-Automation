"""
Human-like behavior simulation to avoid bot detection.

This module provides functions to simulate human behavior patterns:
- Variable typing speed with realistic patterns
- Curved mouse movements (Bezier curves)
- Natural scrolling behavior with momentum
- Random pauses between actions
- Browser fingerprinting evasion
- Realistic viewport and user agent rotation
- Simulated user mistakes and corrections
- Tab switching behavior
"""
import random
import time
import math
from typing import Optional, List, Tuple


def human_typing(page, selector: str, text: str, min_delay: float = 0.05, max_delay: float = 0.15):
    """
    Simulate human typing with variable speed, occasional mistakes, and corrections.

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
    i = 0
    while i < len(text):
        char = text[i]
        page.type(selector, char, delay=random.uniform(min_delay, max_delay))
        
        # Occasional longer pause (simulating thinking)
        if random.random() < 0.05:  # 5% chance
            time.sleep(random.uniform(0.3, 0.8))
        
        # Simulate typing mistake and correction (10% chance on certain characters)
        if random.random() < 0.1 and i > 0 and len(text) > 3:
            # Type wrong character
            wrong_char = random.choice('qwertyuiopasdfghjklzxcvbnm')
            page.type(selector, wrong_char, delay=random.uniform(min_delay, max_delay))
            time.sleep(random.uniform(0.1, 0.3))
            # Backspace to correct
            page.keyboard.press('Backspace')
            time.sleep(random.uniform(0.1, 0.2))
        
        i += 1


def random_mouse_movement(page):
    """
    Simulate random mouse movement to look natural with curved paths.

    Args:
        page: Playwright page object
    """
    try:
        # Get viewport dimensions
        viewport = page.viewport_size
        if viewport:
            start_x = random.randint(100, viewport['width'] - 100)
            start_y = random.randint(100, viewport['height'] - 100)
            end_x = random.randint(100, viewport['width'] - 100)
            end_y = random.randint(100, viewport['height'] - 100)
            
            # Use curved path (Bezier curve simulation)
            control_x = random.randint(100, viewport['width'] - 100)
            control_y = random.randint(100, viewport['height'] - 100)
            
            _bezier_mouse_move(page, start_x, start_y, control_x, control_y, end_x, end_y)
            time.sleep(random.uniform(0.1, 0.3))
    except:
        pass


def _bezier_mouse_move(page, x0: int, y0: int, x1: int, y1: int, x2: int, y2: int, steps: int = 10):
    """
    Move mouse along a quadratic Bezier curve for natural-looking movement.

    Args:
        page: Playwright page object
        x0, y0: Start coordinates
        x1, y1: Control point coordinates
        x2, y2: End coordinates
        steps: Number of intermediate points
    """
    for i in range(steps + 1):
        t = i / steps
        # Quadratic Bezier formula
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t ** 2 * x2
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t ** 2 * y2
        page.mouse.move(int(x), int(y))
        time.sleep(random.uniform(0.01, 0.03))


def natural_scroll(page, direction: str = 'down', amount: int = None):
    """
    Simulate natural scrolling behavior with momentum and random stops.

    Args:
        page: Playwright page object
        direction: 'up' or 'down'
        amount: Pixels to scroll (random if None)
    """
    if amount is None:
        amount = random.randint(200, 500)

    # Scroll in small increments for natural feel with momentum
    steps = random.randint(3, 5)
    step_size = amount // steps

    for i in range(steps):
        # Vary speed - faster at start, slower at end (momentum)
        speed_multiplier = 1.0 - (i / steps) * 0.5
        current_step = int(step_size * speed_multiplier)
        
        page.mouse.wheel(0, current_step if direction == 'down' else -current_step)
        time.sleep(random.uniform(0.1, 0.2))
        
        # Occasional pause mid-scroll (reading)
        if random.random() < 0.2:
            time.sleep(random.uniform(0.3, 0.6))


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
    Configure browser context with human-like settings and anti-detection measures.

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
            {'width': 1536, 'height': 864},
        ]))

    # Set realistic user agent with rotation
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    
    # Set anti-detection headers
    context.set_extra_http_headers({
        'User-Agent': random.choice(user_agents),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    })
    
    # Hide webdriver properties
    context.add_init_script("""
        // Hide webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Override permissions API
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Spoof plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Spoof languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """)


def simulate_tab_switching(page, min_tabs: int = 1, max_tabs: int = 3):
    """
    Simulate tab switching behavior to look like a real user multitasking.

    Args:
        page: Playwright page object
        min_tabs: Minimum number of tab switches
        max_tabs: Maximum number of tab switches
    """
    num_switches = random.randint(min_tabs, max_tabs)
    for _ in range(num_switches):
        # Minimize window (simulating alt-tab)
        try:
            page.evaluate("() => window.blur()")
            time.sleep(random.uniform(0.5, 2.0))
            # Bring back focus
            page.evaluate("() => window.focus()")
            time.sleep(random.uniform(0.3, 1.0))
        except:
            pass


def simulate_reading_pattern(page, text_length: int = 1000):
    """
    Simulate realistic reading pattern with variable speed and scroll-back.

    Args:
        page: Playwright page object
        text_length: Approximate length of text to read
    """
    # Reading speed: ~200-300 words per minute (~3-5 chars per second)
    base_reading_time = text_length / random.uniform(3, 5)
    
    # Break into chunks with pauses
    chunks = random.randint(2, 4)
    chunk_time = base_reading_time / chunks
    
    for i in range(chunks):
        time.sleep(chunk_time)
        
        # Occasional scroll back to re-read (20% chance)
        if random.random() < 0.2:
            page.mouse.wheel(0, -random.randint(50, 150))
            time.sleep(random.uniform(0.3, 0.6))
            page.mouse.wheel(0, random.randint(50, 150))
            time.sleep(random.uniform(0.2, 0.4))


def random_hover_action(page, selector: str = None):
    """
    Randomly hover over elements to simulate exploration.

    Args:
        page: Playwright page object
        selector: Specific selector to hover (optional)
    """
    if selector:
        try:
            page.locator(selector).hover()
            time.sleep(random.uniform(0.2, 0.5))
        except:
            pass
    else:
        # Random mouse movement with hover effect
        random_mouse_movement(page)


def simulate_idle_time(min_seconds: float = 2.0, max_seconds: float = 5.0):
    """
    Simulate idle time where user is doing nothing (thinking, looking away).

    Args:
        min_seconds: Minimum idle time
        max_seconds: Maximum idle time
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def variable_rate_limit(min_delay: float = 5.0, max_delay: float = 15.0):
    """
    Variable rate limiting to avoid detection patterns.

    Args:
        min_delay: Minimum delay between actions
        max_delay: Maximum delay between actions
    """
    # Use exponential distribution for more realistic intervals
    # More short delays, fewer long delays
    base_delay = random.uniform(min_delay, max_delay)
    jitter = random.uniform(0.5, 1.5)
    final_delay = base_delay * jitter
    time.sleep(final_delay)
