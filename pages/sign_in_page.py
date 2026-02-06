from playwright.sync_api import Page

from pages.base_page import BasePage


class SignInPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.sign_up_link= page.locator("//span[@data-testid='signin-switch-to-signup-link']")
        self.email_input = page.locator("//input[@data-testid='input-field-control-email']")
        self.password_input = page.locator("//input[@data-testid='input-field-control-password']")
        self.sign_in_button = page.locator("//button[@data-testid='signin-submit-btn']")

    def click_sign_in(self):
        self.sign_in_button.click()

    def click_sign_up(self):
        self.sign_up_link.click()

    def fill_login_form(self, user_data):
        self.email_input.fill(user_data["email"])
        self.password_input.fill(user_data["password"])



