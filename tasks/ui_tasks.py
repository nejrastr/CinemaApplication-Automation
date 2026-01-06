import json
import os
import re
from asyncio import wait_for

import allure
from bs4 import BeautifulSoup
from mailslurp_client import Configuration, ApiClient, InboxControllerApi, WaitForControllerApi
from playwright.sync_api import expect

from config.settings import BASE_URL
from pages.navbar import Navbar
from pages.registration_page import RegistrationPage
from pages.sign_in_page import SignInPage
from pages.upcoming_movies_page import UpcomingMoviesPage
from pages.currently_showing_page import CurrentlyShowingMoviesPage

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "./data")
REGISTERED_USER_FILE = os.path.join(DATA_FOLDER, "registrated_user.json")

TEST_INBOX_ID = "855cbda0-642a-4134-8987-c8c8d391ca93"
TEST_EMAIL_ADDRESS = "855cbda0-642a-4134-8987-c8c8d391ca93@mailslurp.biz"


class Tasks:

    def __init__(self, page):
        self.page = page
        self.sign_in_page = SignInPage(page)
        self.registration_page = RegistrationPage(page)
        self.upcoming_movies_page = UpcomingMoviesPage(page)
        self.current_showing_page = CurrentlyShowingMoviesPage(page)
        self.navbar = Navbar(page)
        self.base_url = BASE_URL

        MAILSLURP_API_KEY = os.environ.get("MAILSLURP_API_KEY")
        if not MAILSLURP_API_KEY:
            raise ValueError("MAILSLURP_API_KEY environment variable is not set")

        configuration = Configuration()
        configuration.api_key['x-api-key'] = MAILSLURP_API_KEY
        api_client = ApiClient(configuration=configuration)
        self.inbox_controller = InboxControllerApi(api_client)
        self.wait_controller = WaitForControllerApi(api_client)

    @allure.step("Register new user and verify email via MailSlurp")
    def complete_registration(self, user_data):

        test_email = TEST_EMAIL_ADDRESS
        user_data['email'] = test_email

        self.page.goto(self.base_url)
        self.navbar.click_sign_in()
        self.sign_in_page.click_sign_up()
        self.registration_page.fill_registration_form(user_data)
        self.registration_page.click_sign_up()

        with allure.step("Wait for activation email and extract code"):
            email = self.wait_controller.wait_for_latest_email(
                inbox_id=TEST_INBOX_ID,
                timeout=60000,
            )
            soup = BeautifulSoup(email.body, 'html.parser')
            code_label = soup.find('p', string=lambda text: text and 'Your Activation Code' in text)
            if not code_label:
                raise ValueError("'Your Activation Code' label not found in email")

            code_p = code_label.find_next_sibling('p')
            if not code_p:
                raise ValueError("Activation code <p> not found after label")
            activation_code = code_p.get_text(strip=True)

        self.registration_page.fill_verification_code(activation_code)
        self.registration_page.click_continue()
        self.registration_page.verify_registration_form()
        self.registration_page.click_back()

        os.makedirs(DATA_FOLDER, exist_ok=True)
        with open(REGISTERED_USER_FILE, "w") as f:
            json.dump(user_data, f, indent=4)

    @allure.step("Login as user")
    def complete_login(self, user_data):
        self.navbar.click_sign_in()
        allure.dynamic.description(f"Logging in with {user_data['email']}")
        self.sign_in_page.fill_login_form(user_data)
        self.sign_in_page.click_sign_in()
        self.navbar.user_dropdown.wait_for(state="visible")

    @allure.step("Logout from account")
    def complete_logout(self):
        self.navbar.click_user_dropdown()
        self.navbar.click_logout()
        expect(self.navbar.sign_in_button).to_be_visible()

    @allure.step("Select date range in calendar")
    def select_date_range(self, start_date_str, end_date_str):

        self.upcoming_movies_page.click_date_dropdown()

        with allure.step(f"Navigate to and select start date: {start_date_str}"):
            attempts = 0
            while not self.upcoming_movies_page.is_date_visible(start_date_str) and attempts < 12:
                self.upcoming_movies_page.click_date_next()
                attempts += 1
            self.upcoming_movies_page.select_date(start_date_str).click()

        with allure.step(f"Navigate to and select end date: {end_date_str}"):
            attempts = 0
            while not self.upcoming_movies_page.is_date_visible(end_date_str) and attempts < 12:
                self.upcoming_movies_page.click_date_next()
                attempts += 1
            self.upcoming_movies_page.select_date(end_date_str).click()

        self.upcoming_movies_page.click_date_apply()

    @allure.step("Smoke Test: Filter Upcoming Movies")
    def verify_search_and_filtering_upcoming_movies(self, city, cinema, genre, search_term, start_date_val,
                                                    end_date_val, start_date_aria, end_date_aria):

        self.page.goto(self.base_url)
        self.navbar.click_upcoming_movies()

        with allure.step("Apply search and verify card count"):
            self.upcoming_movies_page.fill_search_bar(search_term)
            expect(self.upcoming_movies_page.cards).to_have_count(1)
            expect(self.page).to_have_url(re.compile(f".*title={search_term}.*"))

        with allure.step("Apply location and genre filters"):
            self.upcoming_movies_page.select_city(city, self.page)
            expect(self.page).to_have_url(re.compile(f".*city={city}.*"))
            self.upcoming_movies_page.select_cinema(cinema, self.page)
            expect(self.page).to_have_url(re.compile(rf".*venue={cinema.replace(' ', '[ +]')}.*"))
            self.upcoming_movies_page.select_genre(genre, self.page)
            expect(self.page).to_have_url(re.compile(f".*genre={genre}.*"))

        for card in self.upcoming_movies_page.cards.all():
            expect(card).to_contain_text(genre)

        self.select_date_range(start_date_aria, end_date_aria)
        expect(self.page).to_have_url(re.compile(f".*startDate={start_date_val}.*"))
        expect(self.page).to_have_url(re.compile(f".*endDate={end_date_val}.*"))

    @allure.step("Smoke Test: Filter Currently Showing")
    def verify_search_and_filtering_currently_showing(self, city, cinema, genre, search_term, projection, month, day, weekday, date_val):

        self.page.goto(self.base_url)
        self.navbar.click_currently_showing_link()

        with allure.step("Apply search and location filters"):
            self.current_showing_page.fill_search_bar(search_term)
            expect(self.current_showing_page.cards).to_have_count(1)
            expect(self.page).to_have_url(re.compile(f".*title={search_term}.*"))

            self.current_showing_page.select_city(city, self.page)
            expect(self.page).to_have_url(re.compile(f".*city={city}.*"))
            self.current_showing_page.select_cinema(cinema, self.page)
            expect(self.page).to_have_url(re.compile(rf".*venue={cinema.replace(' ', '[ +]')}.*"))

        with allure.step("Apply genre and projection time"):
            self.current_showing_page.select_genre(genre, self.page)
            expect(self.page).to_have_url(re.compile(f".*genre={genre}.*"))

            self.current_showing_page.select_projection(projection, self.page)
            encoded_time = projection.replace(':', '%3A')
            expect(self.page).to_have_url(re.compile(f".*time={encoded_time}.*"))

            self.current_showing_page.select_date_chip(month, day, weekday)
            expect(self.page).to_have_url(re.compile(f".*date={date_val}.*"))
