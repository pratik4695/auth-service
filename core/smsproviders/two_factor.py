import logging
import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

URL_OTP = "http://2factor.in/API/V1/{}/SMS/{}/{}/{}"
API_KEY = "e4844159-9e17-11ec-a4c2-0200cd936042"


def send_message(url, payload):
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    response = requests.get(url, data=payload, headers=headers)
    logger.info(response.text)


def send_otp(_to, otp, template_id="MYSTOX"):
    url = URL_OTP.format(API_KEY,_to, otp, template_id)
    send_message(url, payload="")
