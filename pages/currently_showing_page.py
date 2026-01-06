from pages.base_page import BasePage
from playwright.sync_api import Page
import re


class CurrentlyShowingMoviesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.search_bar = page.get_by_role("textbox", name="Search Movies")
        self.cities_dropdown = page.locator("div.border:has(span:text('All cities'))")
        self.cinemas_dropdown = page.locator(
            "div.border:has(span:text('All cinemas'))")
        self.genres_dropdown = page.locator("div.border:has(span:has-text('All genres'))")
        self.projections_dropdown = page.locator("div.border:has(span:has-text('All projections'))")
        self.cards = page.locator('div.grid.grid-cols-1.md\\:grid-cols-12')


    def fill_search_bar(self, search_term):
        self.fill(self.search_bar, search_term)
        self.page.wait_for_load_state(state="domcontentloaded")

    def click_cities_dropdown(self):
        self.click(self.cities_dropdown)

    def select_city(self, city_name, page):
        self.click(self.cities_dropdown)
        self.click(page.locator(f"ul li:text('{city_name}')"))

    def select_cinema(self, cinema_name, page):
        self.click(self.cinemas_dropdown)
        self.click(page.locator(f"ul li:text('{cinema_name}')"))

    def select_genre(self, genre, page):
        self.click(self.genres_dropdown)
        self.click(page.locator(f"ul li:text('{genre}')"))

    def select_projection(self, projection, page):
        self.click(self.projections_dropdown)
        self.click(page.locator(f"ul li:text('{projection}')"))

    def select_date_chip(self, month, day, weekday):
      date_button = self.page.locator("button").filter(has_text=re.compile(f"{month}\\s*{day}\\s*{weekday}", re.IGNORECASE))
      date_button.click()









