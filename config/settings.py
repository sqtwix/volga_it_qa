import os
from dataclasses import dataclass

@dataclass
class TimeoutSettings:
    '''Таймайты для ожиданий'''
    DEFAULT: float = 10.0
    PAGE_LOAD: float = 20.0


@dataclass
class UrlSettings:
    '''URL страниц для тестирования'''
    BASE_URL: str = os.getenv('BASE_URL', 'https://practice-automation.com')
    CALENDAR_URL: str = f'{BASE_URL}/calendars/'
    MODAL_URL: str = f'{BASE_URL}/modals/'
    ADS_URL: str = f'{BASE_URL}/ads/'

class Settings:
    timeouts = TimeoutSettings()
    urls = UrlSettings()


settings = Settings()