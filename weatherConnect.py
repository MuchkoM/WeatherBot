from apixu.client import ApixuClient, ApixuException
from config import apixukey
import logging

logger = logging.getLogger(__name__)


def get_temp(current):
    return current['current']['temp_c']


def get_weather_data(place):
    client = ApixuClient(apixukey)
    try:
        current = client.getCurrentWeather(q=place)
        res = place, get_temp(current)
    except ApixuException:
        res = None
    return res
