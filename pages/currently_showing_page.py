from pygments.lexers.robotframework import normalize

from pages.base_page import BasePage
from playwright.sync_api import Page
import re

class CurrentlyShowingMoviesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.search_bar = page.locator("//input[@data-testid='search-input-field']")
        self.cities_dropdown = page.locator("//div[@data-testid='select-trigger-all-cities']")
        self.cinemas_dropdown = page.locator("//div[@data-testid='select-trigger-all-cinemas']")
        self.genres_dropdown = page.locator("//div[@data-testid='select-trigger-all-genres']")
        self.projections_dropdown = page.locator("//div[@data-testid='select-trigger-all-projections']")
        self.cards = page.locator('div.grid.grid-cols-1.md\\:grid-cols-12')

    def click_movie_card(self, movie_name: str):
        normalized = movie_name.lower().replace(" ", "-")

        card = self.page.locator(f"//div[@data-testid='movie-card-{normalized}']")
        card.wait_for(state="visible")
        self.click(card)

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
      date_button = self.page.locator("button").filter(has_text=re.compile(f"{month}\\s*{day}\\s*{weekday[:3]}", re.IGNORECASE))
      date_button.click()