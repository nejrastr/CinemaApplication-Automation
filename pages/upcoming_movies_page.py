from pages.base_page import BasePage
from playwright.sync_api import Page


class UpcomingMoviesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.search_bar = page.get_by_role("textbox", name="Search Movies")
        self.cities_dropdown = page.locator("div.border:has(span:text('All cities'))")
        self.cinemas_dropdown = page.locator(
            "div.border:has(span:text('All cinemas'))")
        self.genres_dropdown = page.locator("div.border:has(span:has-text('All genres'))")
        self.date_range_dropdown = page.locator("div.border:has(span:text('Date Range'))")
        self.date_picker_apply_button = page.get_by_role("button", name="Apply")
        self.date_picker_next = page.locator("button[aria-label='Next Month']")
        self.date_picker_previous = page.locator("button[aria-label='Previous Month']")
        self.cards = page.locator("div.grid > div.bg-neutral-0.border.rounded-2xl.shadow-card")

    def select_date(self, date_str):
        return self.page.locator(f"div[aria-label='Choose {date_str}']")
    def click_date_next(self):
        self.click(self.date_picker_next)
    def click_date_previous(self):
        self.click(self.date_picker_previous)
    def click_date_apply(self):
        self.click(self.date_picker_apply_button)

    def click_date_dropdown(self):
        self.click(self.date_range_dropdown)

    def is_date_visible(self, date_str):
        return self.page.locator(f"div[aria-label*='{date_str}']").is_visible()

    def click_next_month(self):
        self.date_picker_next.click()



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









