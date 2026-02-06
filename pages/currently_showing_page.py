from pages.base_page import BasePage
from playwright.sync_api import Page, expect

class CurrentlyShowingMoviesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.search_bar = page.locator("//input[@data-testid='search-input-field']")
        self.cities_dropdown = page.locator("//div[@data-testid='select-trigger-all-cities']")
        self.cinemas_dropdown = page.locator("//div[@data-testid='select-trigger-all-cinemas']")
        self.genres_dropdown = page.locator("//div[@data-testid='select-trigger-all-genres']")
        self.projections_dropdown = page.locator("//div[@data-testid='select-trigger-all-projections']")
        self.cards = page.locator('div.grid.grid-cols-1.md\\:grid-cols-12')
        self.city_list = page.get_by_test_id("select-options-list-all-cities")

    def click_movie_card(self, movie_name: str):
        movie_slug = movie_name.lower().replace(":", "").replace(" ", "-")
        movie_card = self.page.locator(f"div.grid:has(h1[data-testid='movie-card-title-{movie_slug}'])")
        movie_card.wait_for(state="visible")
        self.click(movie_card)

    def fill_search_bar(self, search_term):
        self.fill(self.search_bar, search_term)
        self.page.wait_for_load_state(state="domcontentloaded")

    def click_cities_dropdown(self):
        self.click(self.cities_dropdown)

    def select_city(self, city_name, page):
        self.click(self.cities_dropdown)
        self.page.wait_for_timeout(500)
        expect(self.city_list).to_be_visible(timeout=5000)
        city_slug = city_name.strip().lower().replace(" ", "-")
        target_option = page.locator(f"li[data-testid*='select-option-all-cities-{city_slug}']")
        target_option.click()
        expect(self.city_list).to_be_hidden(timeout=3000)

    def select_cinema(self, cinema_name, page):
        self.click(self.cinemas_dropdown)
        self.page.wait_for_timeout(500)
        cinema_slug = cinema_name.strip().lower().replace(" ", "-")
        target_option = page.locator(f"li[data-testid*='select-option-all-cinemas-{cinema_slug}']")
        target_option.click()

    def select_genre(self, genre, page):
        self.click(self.genres_dropdown)
        self.click(page.locator(f"ul li:text('{genre}')"))

    def select_projection(self, projection, page):
        self.click(self.projections_dropdown)
        self.click(page.locator(f"ul li:text('{projection}')"))

    def select_date_chip(self, month, day, weekday):
        ui_day = day.lstrip('0')
        date_button = self.page.locator("button").filter(has_text=month).filter(has_text=ui_day)
        date_button.scroll_into_view_if_needed()
        expect(date_button).to_be_visible(timeout=10000)
        date_button.click()