import re
from django.core.exceptions import ValidationError
from dotenv import load_dotenv
import os
import requests
import json
from .constants import SMS_API_URL, TEMPLATE_ID


def validate_phone_number(phone_number: str):
    # regex for iranian phone numbers: https://stackoverflow.com/a/18618958/15706468

    regex = r"(0|\+98)?([ ]|-|[()]){0,2}9[0-9]([ ]|-|[()]){0,2}(?:[0-9]([ ]|-|[()]){0,2}){8}"

    match_phone_number = re.match(regex, phone_number)
    if not match_phone_number:
        raise ValidationError(f"{phone_number} is not valid phone number!")


def is_phone_number_valid(phone_number: str):

    regex = r"(0|\+98)?([ ]|-|[()]){0,2}9[0-9]([ ]|-|[()]){0,2}(?:[0-9]([ ]|-|[()]){0,2}){8}"

    match_phone_number = re.match(regex, phone_number)
    if not match_phone_number:
        return False

    return True


def is_valid_otp(otp: str):
    pattern = r'^\d{6}$'
    return re.fullmatch(pattern, otp) is not None


def send_sms(phone_number: str, code: str):
    load_dotenv()
    sms_key = os.getenv('SMS_API_KEY_SANDBOX')

    header = {
        'Content-Type': 'application/json',
        'Accept': 'text/plain',
        'x-api-key': sms_key
    }

    body = {
        "mobile": f"{phone_number}",
        "templateId": TEMPLATE_ID,
        "parameters": [
            {
                "name": "Code",
                "value": f"{code}"
            }
        ]
    }

    response = requests.post(SMS_API_URL, headers=header, json=body)

    return response.status_code == 200

    




