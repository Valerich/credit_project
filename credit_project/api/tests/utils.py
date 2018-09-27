import datetime
import pytz

from django.conf import settings


def build_absolute_url(url):
    return 'http://testserver' + url


def get_tz_datetime(year, month=1, day=1, hour=0, minute=0, second=0):
    tz = pytz.timezone(getattr(settings, 'TIME_ZONE', 'Europe/Moscow'))
    return datetime.datetime(year, month, day, hour, minute, second).astimezone(tz)
