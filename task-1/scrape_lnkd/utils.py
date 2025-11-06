import os
import time
import math
import re
from pathlib import Path
from urllib.parse import urlparse
from random import uniform
from typing import Optional

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_driver() -> RemoteWebDriver:
    """
    Start a Chrome WebDriver using webdriver_manager.
    - Non-headless for now
    - Sets window size to 1280x900
    - Applies a few sane defaults
    """
    chrome_options = Options()
    # Non-headless (omit --headless)
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1280, 900)
    return driver


def login(driver: RemoteWebDriver) -> None:
    """
    Log in to LinkedIn using credentials from .env (LI_EMAIL, LI_PASS).
    If MFA appears, complete it manually in the opened browser; this function
    waits until a known post-login element is present.
    """
    load_dotenv()
    email = os.getenv("LI_EMAIL")
    password = os.getenv("LI_PASS")
    if not email or not password:
        raise RuntimeError("Missing LI_EMAIL or LI_PASS in environment (.env).")

    driver.get("https://www.linkedin.com/login")

    # Fill and submit the login form
    email_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    password_input = driver.find_element(By.ID, "password")

    email_input.clear()
    email_input.send_keys(email)
    password_input.clear()
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

    # Wait for a post-login element; allow time for MFA if it appears
    # Any of these indicate we are in the authenticated experience
    post_login_locators = [
        (By.ID, "global-nav"),
        (By.CSS_SELECTOR, "input[placeholder='Search']"),
        (By.CSS_SELECTOR, "div.search-global-typeahead"),
    ]

    def any_present(drv) -> Optional[object]:
        for by, sel in post_login_locators:
            try:
                el = drv.find_element(by, sel)
                if el:
                    return el
            except Exception:
                continue
        return None

    # Up to 120s to allow manual MFA completion
    WebDriverWait(driver, 120).until(lambda d: any_present(d))


def human_scroll(driver: RemoteWebDriver, total_pause_sec: float = 4) -> None:
    """
    Scroll to bottom in small increments with short, human-like pauses.
    Intended to be reused on feed or profile pages.
    """
    # Determine number of steps between 6 and 10 based on page height
    try:
        total_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);")
        viewport_h = driver.execute_script("return window.innerHeight;")
    except Exception:
        total_height = 3000
        viewport_h = 800

    steps = max(6, min(10, math.ceil(total_height / max(viewport_h, 1))))
    step_distance = max(int(total_height / steps), 200)

    for _ in range(steps):
        driver.execute_script("window.scrollBy(0, arguments[0]);", step_distance)
        time.sleep((total_pause_sec / steps) + uniform(0.05, 0.3))

    # Ensure we reach the bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(uniform(0.2, 0.6))

def read_urls(path: str = "urls.txt") -> list[str]:
    urls: list[str] = []
    if not os.path.exists(path):
        return urls
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            urls.append(s)
    return urls


def wait_for_profile_loaded(driver: RemoteWebDriver, timeout: int = 20) -> None:
    """
    Wait until a LinkedIn profile is reasonably loaded.
    Success criteria (any):
      - A visible non-empty main h1 (profile name)
      - Section headers containing 'About' or 'Experience'
    """
    def page_ready(drv) -> bool:
        # 1) Try to find a visible non-empty main h1
        try:
            h1_candidates = drv.find_elements(By.CSS_SELECTOR, "main h1")
            if not h1_candidates:
                h1_candidates = drv.find_elements(By.TAG_NAME, "h1")
            for el in h1_candidates:
                if el.is_displayed() and el.text.strip():
                    return True
        except Exception:
            pass

        # 2) Look for "About" or "Experience" in section headers
        try:
            about_xpath = "//section//*[normalize-space()='About']"
            exp_xpath = "//section//*[normalize-space()='Experience']"
            for xpath in [about_xpath, exp_xpath]:
                markers = drv.find_elements(By.XPATH, xpath)
                for el in markers:
                    if el.is_displayed():
                        return True
        except Exception:
            pass
        return False

    WebDriverWait(driver, timeout).until(lambda d: page_ready(d))


def save_html(driver: RemoteWebDriver, url: str, out_dir: str = "html_dumps") -> str:
    """
    Save current page HTML to html_dumps/<slug>.html.
    Slug is derived from the LinkedIn /in/<slug> path when possible.
    """
    # Ensure directory exists
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    # Derive a reasonable filename from the URL
    parsed = urlparse(url)
    path = parsed.path or ""
    slug = ""
    # Prefer /in/<slug>
    if "/in/" in path:
        after = path.split("/in/", 1)[1]
        slug = after.split("/", 1)[0]
    if not slug:
        # fallback: last non-empty segment of the path
        parts = [p for p in path.split("/") if p]
        if parts:
            slug = parts[-1]
    if not slug:
        # final fallback: sanitize hostname + path
        slug = f"{parsed.netloc}{path}"
    # Clean slug to filesystem-safe
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", slug).strip("-").lower() or "profile"

    # Nudge content to load, then capture
    human_scroll(driver, total_pause_sec=4)
    html = driver.page_source

    out_path = str(Path(out_dir) / f"{slug}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path