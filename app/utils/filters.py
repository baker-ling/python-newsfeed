from datetime import datetime


from datetime import datetime


def format_date(date: datetime) -> str:
    return date.strftime("%m/%d/%y")


def format_url(url: str) -> str:
    return url.replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0].split("?")[0]


def format_plural(amount, word):
    if amount != 1:
        return word + "s"
    return word
