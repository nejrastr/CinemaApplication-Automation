from playwright.sync_api import Page
from pages.base_page import BasePage

class StripePaymentPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.payment_submit_button = page.get_by_test_id("payment-submit-button")

    def fill_stripe_input(self, input_name, value):
        for iframe in self.page.locator("iframe").all():
            frame = iframe.content_frame
            if frame is None:
                continue
            input_field = frame.locator(f"input[name='{input_name}']")
            if input_field.count() > 0:
                input_field.fill(value)
                return
        raise RuntimeError(f"Stripe input '{input_name}' not found")

    def fill_payment_details(self, payment_details):
        self.fill_stripe_input("number", payment_details["card_number"])
        self.fill_stripe_input("expiry", payment_details["expiry_date"])
        self.fill_stripe_input("cvc", payment_details["cvv"])

    def click_payment_submit_button(self):
        self.click(self.payment_submit_button)
