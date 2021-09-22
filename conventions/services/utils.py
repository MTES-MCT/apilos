from enum import Enum


def format_date_for_form(date):
    return date.strftime("%Y-%m-%d") if date is not None else ""


class ReturnStatus(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    WARNING = "WARNING"
