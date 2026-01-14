from playwright.sync_api import Page

from pages.base_page import BasePage


class RegistrationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input = page.locator("//input[@name='email']")
        self.password_input = page.locator("//input[@name='password']")
        self.confirm_password_input = page.locator("//input[@name='confirmPassword']")
        self.sign_up_button = page.locator("//button[normalize-space()='Sign Up']")
        self.code_inputs = page.locator("input[autocomplete='one-time-code']")
        self.continue_button = page.get_by_role("button", name="Continue")

        self.back_button = page.locator(
            "div.fixed.top-16.right-0 button:has(svg[data-icon='arrow-left'])"
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
