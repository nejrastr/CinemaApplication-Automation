from playwright.sync_api import Page, Locator, expect

from pages.base_page import BasePage


class Navbar(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.logo = page.locator("//a[.//h1[normalize-space()='Cinebh.']]")
        self.currently_showing_link = page.locator("//a[normalize-space()='Currently Showing']")
        self.upcoming_movies_link = page.locator("//a[normalize-space()='Upcoming Movies']")
        self.sign_in_button = page.locator("//button[text()='Sign In']")
        self.user_dropdown = page.locator("button:has(svg[data-icon='angle-down'])")
        self.logout_button = page.locator("//ul/li[normalize-space()='Logout']")

    def click_sign_in(self):
        self.sign_in_button.click()
    def click_logo(self):
        self.logo.click()
    def click_upcoming_movies(self):
        self.upcoming_movies_link.click()
    def click_currently_showing_link(self):
        self.currently_showing_link.click()
    def click_user_dropdown(self):
        self.click(self.user_dropdown)
    def click_logout(self):
        self.click(self.logout_button)


