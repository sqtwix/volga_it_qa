import os
from dataclasses import dataclass


@dataclass
class TimeoutSettings:
    """Таймауты ожидания элементов и навигации в секундах."""
    DEFAULT: float = 10.0
    PAGE_LOAD: float = 45.0


@dataclass
class UrlSettings:
    """Адреса страниц; BASE_URL читается из окружения при импорте модуля."""
    BASE_URL: str = os.getenv('BASE_URL', 'https://practice-automation.com')
    CALENDAR_URL: str = f'{BASE_URL}/calendars/'
    MODAL_URL: str = f'{BASE_URL}/modals/'
    ADS_URL: str = f'{BASE_URL}/ads/'
    FORM_FIELDS_URL: str = f'{BASE_URL}/form-fields/'


timeouts = TimeoutSettings()
urls = UrlSettings()
