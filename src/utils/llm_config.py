from datetime import datetime

from utils.constants import SYSTEM_MESSAGE


def get_system_prompt() -> str:
    """Give system prompt"""
    today = datetime.now().date()
    return SYSTEM_MESSAGE.format(date=today)
