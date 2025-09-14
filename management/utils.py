import random
import string


def generate_inspection_code(length=12):
    digits = string.digits
    code = "".join(random.choices(digits, k=length))
    return code