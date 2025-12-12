import re
import pytest
from playwright.sync_api import expect

def test_google_search(page):
    page.goto("https://duckduckgo.com/")
    search_box = page.locator("input[name='q']")
    search_box.fill("Klix")
    page.keyboard.press("Enter")
    expect(page).to_have_title(re.compile("Klix", re.IGNORECASE))