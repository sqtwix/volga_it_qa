import os
from dataclasses import dataclass


@dataclass
class TimeoutSettings:
    '''Таймауты для ожиданий'''
    DEFAULT: float = 10.0
    PAGE_LOAD: float = 20.0
    ADS_POPUP: float = 15.0


@dataclass
class UrlSettings:
    '''URL страниц для тестирования'''
    BASE_URL: str = os.getenv('BASE_URL', 'https://practice-automation.com')
    CALENDAR_URL: str = f'{BASE_URL}/calendars/'
    MODAL_URL: str = f'{BASE_URL}/modals/'
    ADS_URL: str = f'{BASE_URL}/ads/'


timeouts = TimeoutSettings()
urls = UrlSettings()
