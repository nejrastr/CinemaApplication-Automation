from playwright.sync_api import Page
from pages.base_page import BasePage

class StripePaymentPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.payment_submit_button = page.get_by_test_id("payment-submit-button")

    def fill_stripe_input(self, input_name, value):
        input_field = self.page.frame_locator("iframe[name^='__privateStripeFrame']") \
            .first.locator(f"input[name='{input_name}']")
        input_field.wait_for(state="visible", timeout=15000)
        input_field.fill(value)

    def fill_payment_details(self, payment_details):
        self.fill_stripe_input("number", payment_details["card_number"])
        self.fill_stripe_input("expiry", payment_details["expiry_date"])
        self.fill_stripe_input("cvc", payment_details["cvv"])

    def click_payment_submit_button(self):
        self.click(self.payment_submit_button)