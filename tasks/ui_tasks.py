import os
import re
import time
import allure
from playwright.sync_api import expect
from utils.email_util import EmailHelper
from config.settings import BASE_URL
from pages.navbar import Navbar
from pages.registration_page import RegistrationPage
from pages.sign_in_page import SignInPage
from pages.upcoming_movies_page import UpcomingMoviesPage
from pages.currently_showing_page import CurrentlyShowingMoviesPage
from utils.logger import log_info


class Tasks:

    def __init__(self, page):
        self.page = page
        self.sign_in_page = SignInPage(page)
        self.registration_page = RegistrationPage(page)
        self.upcoming_movies_page = UpcomingMoviesPage(page)
        self.current_showing_page = CurrentlyShowingMoviesPage(page)
        self.navbar = Navbar(page)
        self.base_url = BASE_URL
        self.app_password = os.getenv("GMAIL_APP_PASSWORD")

    @allure.step("Register and Verify via Gmail")
    def complete_registration(self, user_data):
        timestamp = int(time.time())
        unique_email = f"strsevicnejra+{timestamp}@gmail.com"
        user_data['email'] = unique_email

        log_info(f"Navigating to {self.base_url} for registration")
        self.page.goto(self.base_url)

        log_info("Navigating to Sign Up form")
        self.navbar.click_sign_in()
        self.sign_in_page.click_sign_up()

        log_info(f"Filling registration form for: {unique_email}")
        self.registration_page.fill_registration_form(user_data)
        self.registration_page.click_sign_up()

        log_info("Fetching verification code from Gmail...")
        with allure.step(f"Fetch code for {unique_email}"):
            activation_code = EmailHelper.get_verification_code(unique_email, self.app_password)
            log_info(f"Extracted code: {activation_code}")

        log_info("Entering verification code and finalizing registration")
        self.registration_page.fill_verification_code(activation_code)
        self.registration_page.click_continue()

    @allure.step("Login as user")
    def complete_login(self, user_data):
        log_info(f"Attempting UI login for user: {user_data['email']}")
        self.navbar.click_sign_in()
        allure.dynamic.description(f"Logging in with {user_data['email']}")

        self.sign_in_page.fill_login_form(user_data)
        self.sign_in_page.click_sign_in()

        self.navbar.user_dropdown.wait_for(state="visible")
        log_info("Login successful - user dropdown is visible")

    @allure.step("Logout from account")
    def complete_logout(self):
        log_info("Logging out user via Navbar")
        self.navbar.click_user_dropdown()
        self.navbar.click_logout()
        expect(self.navbar.sign_in_button).to_be_visible()
        log_info("Logout successful - Sign In button visible")

    @allure.step("Select date range in calendar")
    def select_date_range(self, start_date_str, end_date_str):
        log_info(f"Opening calendar to select range: {start_date_str} to {end_date_str}")
        self.upcoming_movies_page.click_date_dropdown()

        with allure.step(f"Navigate to and select start date: {start_date_str}"):
            attempts = 0
            while not self.upcoming_movies_page.is_date_visible(start_date_str) and attempts < 12:
                log_info(f"Start date not visible, clicking Next (Attempt {attempts + 1})")
                self.upcoming_movies_page.click_date_next()
                attempts += 1
            self.upcoming_movies_page.select_date(start_date_str).click()

        with allure.step(f"Navigate to and select end date: {end_date_str}"):
            attempts = 0
            while not self.upcoming_movies_page.is_date_visible(end_date_str) and attempts < 12:
                log_info(f"End date not visible, clicking Next (Attempt {attempts + 1})")
                self.upcoming_movies_page.click_date_next()
                attempts += 1
            self.upcoming_movies_page.select_date(end_date_str).click()

        self.upcoming_movies_page.click_date_apply()
        log_info("Date range applied successfully")

    @allure.step("Smoke Test: Filter Upcoming Movies")
    def verify_search_and_filtering_upcoming_movies(self, city, cinema, genre, search_term, start_date_val,
                                                    end_date_val, start_date_aria, end_date_aria):

        log_info(f"Starting Filter Smoke Test for Upcoming Movies: {search_term}")
        self.page.goto(self.base_url)
        self.navbar.click_upcoming_movies()

        with allure.step("Apply search and verify card count"):
            log_info(f"Searching for title: {search_term}")
            self.upcoming_movies_page.fill_search_bar(search_term)
            expect(self.upcoming_movies_page.cards).to_have_count(1)
            expect(self.page).to_have_url(re.compile(f".*title={search_term}.*"))

        with allure.step("Apply location and genre filters"):
            log_info(f"Applying filters: City={city}, Cinema={cinema}, Genre={genre}")
            self.upcoming_movies_page.select_city(city, self.page)
            self.upcoming_movies_page.select_cinema(cinema, self.page)
            self.upcoming_movies_page.select_genre(genre, self.page)

        log_info("Verifying genre text on all visible cards")
        for card in self.upcoming_movies_page.cards.all():
            expect(card).to_contain_text(genre)

        self.select_date_range(start_date_aria, end_date_aria)
        log_info("Verifying URL contains selected date parameters")
        expect(self.page).to_have_url(re.compile(f".*startDate={start_date_val}.*"))
        expect(self.page).to_have_url(re.compile(f".*endDate={end_date_val}.*"))

    @allure.step("Smoke Test: Filter Currently Showing")
    def verify_search_and_filtering_currently_showing(self, city, cinema, genre, search_term, projection, month, day,
                                                      weekday, date_val):

        log_info(f"Starting Currently Showing Smoke Test. Search: {search_term}")
        self.page.goto(self.base_url)
        self.navbar.click_currently_showing_link()

        with allure.step("Apply search and location filters"):
            log_info(f"Filtering by title: {search_term} and location: {city}")
            self.current_showing_page.fill_search_bar(search_term)
            self.current_showing_page.select_city(city, self.page)
            self.current_showing_page.select_cinema(cinema, self.page)

        with allure.step("Apply genre and projection time"):
            log_info(f"Filtering by genre: {genre} and time: {projection}")
            self.current_showing_page.select_genre(genre, self.page)
            self.current_showing_page.select_projection(projection, self.page)

            log_info(f"Selecting date chip: {weekday} {month} {day}")
            self.current_showing_page.select_date_chip(month, day, weekday)

        log_info(f"Final URL verification for date: {date_val}")
        expect(self.page).to_have_url(re.compile(f".*date={date_val}.*"))