import logging
import allure


def get_logger(name=__name__):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger


def log_info(message):
    logger = get_logger()
    logger.info(message)
    allure.attach(message, name="Log", attachment_type=allure.attachment_type.TEXT)