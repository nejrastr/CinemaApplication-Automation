import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

class ReservationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.movie_title = page.get_by_test_id("booking-movie-title")
        self.booking_details_venue = page.get_by_test_id("booking-projection-venue")
        self.booking_details_time = page.get_by_test_id("booking-projection-date-time")
        self.session_initialized = page.get_by_test_id("booking-layout-session-timer")

        self.seats_container = page.get_by_test_id("seat-map-section")
        self.selected_seats_list = page.get_by_test_id("selected-seats-list")
        self.total_price = page.get_by_test_id("total-price-amount")
        self.confirm_button = page.get_by_test_id("seat-booking-continue-button")
        self.reservation_success_message = page.get_by_test_id("reservation-success-message")

    def verify_reservation_success(self):
        self.reservation_success_message.is_visible()

    def verify_session_timer(self):
        expect(self.session_initialized).to_be_visible()

    def verify_booking_details(self, movie_title, cinema_name, time_str):
        expect(self.movie_title).to_contain_text(movie_title)
        expect(self.booking_details_venue).to_contain_text(cinema_name)
        expect(self.booking_details_time).to_contain_text(time_str)

    def select_seat(self, seat_number: str):
        seat = self.seats_container.locator("div").filter(has_text=seat_number).first
        seat.click()

    def verify_selection(self, selected_seat: str):
        expect(self.selected_seats_list).to_contain_text(selected_seat)

    def verify_price(self, price: str):
        expect(self.total_price).to_contain_text(price)

    def verify_button_state(self, is_enabled: bool):
        if is_enabled:
            expect(self.confirm_button).to_be_enabled()
        else:
            expect(self.confirm_button).to_be_disabled()

    def complete_reservation(self):
        self.click(self.confirm_button)

    def select_first_available_seat(self) -> str:

        potential_seats = self.seats_container.locator("div").all()

        for seat in potential_seats:
            seat_text = seat.text_content().strip()
            if re.match(r"^[A-Z]\d+$", seat_text):

                class_attr = seat.get_attribute("class") or ""
                if "cursor-not-allowed" not in class_attr and "reserved" not in class_attr:
                    seat.click()
                    return seat_text
        raise RuntimeError("No available seats found on the screen!")