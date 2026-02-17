import random
import string

from app.core.config import settings


def generate_otp(length: int = settings.OTP_LENGTH) -> str:
    return "".join(random.choices(string.digits, k=length))
