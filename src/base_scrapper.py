from abc import ABC, abstractmethod

import requests
from src.logger import setup_logger
logger = setup_logger()


class BaseScraper(ABC):
    """
    Abstract base class for all scraper classes.
    """

    def __init__(self, proxy_manager):
        super().__init__()
        self.proxy_manager = proxy_manager

    @abstractmethod
    def scrape(self, url = None):
        """
        Method to perform the scraping action.
        This must be overridden by all subclasses.

        :param url: URL of the page to scrape, defaults to None.
        :return: A dictionary with the scraped data.
        """
        pass


    def http_get(self, session, url, proxied=False):
        if proxied == True:
            try:
                proxy = self.proxy_manager.get_proxy()
                if proxy is not None:
                    proxies = {"http": proxy, "https": proxy}
                    response = session.get(url, proxies=proxies)
                else:
                    response = session.get(url)

                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if proxied:
                    logger.error(f"Request failed using proxy {proxy}: {e}")
                else:
                    logger.error(f"Request failed: {e}")
        else:
            return session.get(url)
