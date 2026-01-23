from playwright.sync_api import Page, expect
import re

from pages.base_page import BasePage


class MovieDetailsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.header_title = page.get_by_test_id("movie-details-title")
        self.meta_row = page.get_by_test_id("movie-details-info")
        self.synopsis_text = page.get_by_test_id("movie-details-synopsis")
        self.director_label = page.get_by_test_id("movie-details-director-name")
        self.writers_label = page.get_by_test_id("movie-details-writers-container")
        self.genre_badges = page.locator("div.flex.gap-4.mt-2 button")
        self.cast_cards = page.get_by_test_id("movie-details-cast-grid")
        self.cities_dropdown = page.get_by_test_id("select-trigger-choose-city")
        self.cinemas_dropdown = page.get_by_test_id(
            "select-trigger-choose-cinema")
        self.projection_time_buttons = self.page.locator("button[data-testid^='projection-time-']")
        self.reservation_button = page.get_by_test_id("movie-details-reserve-ticket-button")

    def verify_all_content(self, data: dict):

        expect(self.header_title).to_have_text(data['title'])
        expect(self.synopsis_text).to_have_text(data['synopsis'])
        meta_content = self.meta_row.text_content()
        assert data['pgRating'] in meta_content, f"Rating {data['pgRating']} not found in UI"
        assert str(data['duration']) in meta_content, f"Duration {data['duration']} not found"
        raw_genres = self.genre_badges.all_text_contents()
        ui_genres = [g.strip() for g in raw_genres if not any(char.isdigit() for char in g)]


        assert sorted(ui_genres) == sorted(data['genres']), \
            f"Genre mismatch! UI: {ui_genres} vs DB: {data['genres']}"

        for actor in data['cast']:
            actor_card = self.cast_cards \
                .filter(has_text=actor['name']) \
                .filter(has_text=actor['character'])

            expect(actor_card).to_be_visible()
        expect(self.director_label).to_contain_text(data['director'])

        for writer in data['writers']:
            expect(self.writers_label).to_contain_text(writer)

    def click_cities_dropdown(self):
        self.click(self.cities_dropdown)

    def click_cinemas_dropdown(self):
        self.click(self.cinemas_dropdown)

    def select_city(self, city_name: str):
        self.click(self.cities_dropdown)
        self.page.locator("li").filter(has_text=city_name).click()

    def select_cinema(self, cinema_name: str):
        self.click(self.cinemas_dropdown)
        self.page.locator("li").filter(has_text=cinema_name).click()

    def click_reservation_button(self):
        self.click(self.reservation_button)

    def click_first_available_time(self):
        self.projection_time_buttons.first.click()