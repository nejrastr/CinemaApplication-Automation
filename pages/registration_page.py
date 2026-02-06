from playwright.sync_api import Page

from pages.base_page import BasePage


class RegistrationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input = page.locator("//input[@data-testid='input-field-control-email']")
        self.password_input = page.locator("//input[@data-testid='input-field-control-password']")
        self.confirm_password_input = page.locator("//input[@data-testid='input-field-control-confirmPassword']")
        self.sign_up_button = page.locator("//button[@data-testid='signup-submit-btn']")
        self.code_inputs = page.locator("input[autocomplete='one-time-code']")
        self.continue_button = page.locator(
            "//button[@data-testid='verification-submit-btn']")
        self.back_button = page.locator(
            "button//[@data-testid='drawer-close-button']"
        )
    def click_back(self):
        self.back_button.wait_for(state="visible", timeout=5000)
        self.click(self.back_button)

    def click_sign_up(self):
        self.click(self.sign_up_button)

    def fill_registration_form(self, user_data):
        self.fill(self.email_input, user_data['email'])
        self.fill(self.password_input, user_data['password'])
        self.fill(self.confirm_password_input, user_data['confirm_password'])

    def fill_verification_code(self, verification_code):
        for i, digit in enumerate(verification_code):
            self.code_inputs.nth(i).fill(digit)

    def click_continue(self):
        self.click(self.continue_button)
