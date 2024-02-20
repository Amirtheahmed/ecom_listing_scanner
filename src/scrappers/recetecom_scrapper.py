import os

import requests
import json
import re
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from src.base_scrapper import BaseScraper
from src.proxy_manager import ProxyManager
from src.logger import setup_logger
from src.rabbitmq import RabbitMQ

logger = setup_logger()

# Suppress only the single InsecureRequestWarning from urllib3 needed
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Scraper(BaseScraper):
    def __init__(self):
        proxy_manager = ProxyManager()
        self.rabbitmq = RabbitMQ()
        super().__init__(proxy_manager)
        self.proxied = os.environ.get('RECETECOM_PROXIED', False)
        self.base_url = 'https://www.recete.com'
        self.session = requests.Session()

    def remove_escapes(self, text):
        filter_func = ''.join([chr(i) for i in range(1, 32)])
        return text.translate(str.maketrans('', '', filter_func))

    def scrap_page(self, url):
        try:
            response = self.http_get(self.session, url, self.proxied)
            return BeautifulSoup(response.text, "html.parser")
        except requests.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"An error occurred while getting soup: {e}")
        return None

    def parse_json_ld(self, soup):
        json_objects = []
        for script_tag in soup.find_all('script', type='application/ld+json'):
            try:
                json_data = json.loads(script_tag.string.strip())
                json_objects.append(json_data)
            except Exception as e:
                print(f"Error parsing JSON-LD script: {e}")
        return json_objects

    def parse_product_data_script(self, soup):
        product_data_pattern = re.compile(r'PRODUCT_DATA.push\(JSON.parse\(\'({.*?})\'\)\);', re.DOTALL)
        for script in soup.find_all('script'):
            if script.string and "PRODUCT_DATA.push" in script.string:
                match = product_data_pattern.search(script.string)
                if match:
                    try:
                        json_string = match.group(1)
                        json_string = json_string.encode('utf-8').decode('unicode_escape')
                        return json.loads(json_string)
                    except Exception as e:
                        print(f"Error parsing PRODUCT_DATA script: {e}")
        return None

    def get_product_details(self, soup):
        product_data = self.parse_product_data_script(soup)
        json_ld_data = self.parse_json_ld(soup)
        detail_data = next((obj for obj in json_ld_data if obj.get('@type') == 'Product'), None)

        if not product_data or not detail_data:
            return None

        return self.extract_details(product_data, detail_data)

    def extract_details(self, product_data, detail_data):
        return {
            "name": product_data.get('name', None),
            "product_sku": detail_data.get('sku', None),
            "barcode": product_data.get('barcode', None),
            "brand": product_data.get('brand', None),
            "description": detail_data.get('description', None),
            "price_currency": product_data.get('currency', None),
            "price_amount": product_data.get('sale_price', None),
            "url": product_data.get('url', None),
            "image_urls": detail_data.get('image', None),
            "category_path": detail_data.get('category', None),
            "category": product_data['category'].split(',')[-1],
            "root_category_id": None,
            "sub_category_id": product_data.get('category_id', None),
            "stock": product_data.get('quantity', None),
        }

    def prepare_raw_data(self, product_details):
        return {
            "source_channel": "recetecom",
            "source_type": "retailer",
            "main_identifier": product_details.get('product_sku'),
            "listing": product_details
        }

    def get_product_category_urls(self):
        soup = BeautifulSoup(self.http_get(self.session, self.base_url, self.proxied).text, "html.parser")
        main_menu = soup.find('nav', id='main-menu')
        top_level_links = main_menu.find_all('a', href=True)

        category_urls = []
        for link in top_level_links:
            href = link['href']
            path = re.sub(r'^https?://[^/]+/|/$', '', href)
            if path not in ["/firsatlar", "/kampanyalar", "marka-listesi"] and path and not path.startswith(
                    ('#', '?', '/')):
                category_urls.append(self.base_url + '/' + path)

        return category_urls

    def get_product_urls_from_product_category(self, category_url):
        product_url_list = []
        soup = BeautifulSoup(self.http_get(self.session, category_url, self.proxied).text, "html.parser")
        total_products_text = soup.find('div', class_='pagination-info-bar').find('span').text
        total_products = int(total_products_text.replace(" ürün bulunmaktadır.", "")) if total_products_text else 0

        products_per_page = 24
        total_pages = (total_products + products_per_page - 1) // products_per_page
        page_urls = [f"{category_url}?pg={page}" for page in range(1, total_pages + 1)]
        page_urls[0] = category_url  # If the first page has a different URL

        for url in page_urls:
            response = self.http_get(self.session, url, self.proxied)
            soup = BeautifulSoup(response.text, "html.parser")
            product_url_list.extend(self.get_product_urls(soup))

        return product_url_list


    def get_product_urls(self, soup):
        product_containers = soup.find_all('div', class_='product-item')
        product_urls = []

        for container in product_containers:
            a_tag = container.find('a', class_='image-wrapper')
            if a_tag and 'href' in a_tag.attrs:
                full_url = self.base_url + a_tag['href']
                product_urls.append(full_url)

        return product_urls

    async def scrape(self, url = None):
        if url:
            soup = self.scrap_page(url)
            if soup:
                raw_data = self.prepare_raw_data(self.get_product_details(soup))
                self.rabbitmq.publish(body=raw_data)

            return None
        if not url:
            logger.info(" \t\u2714 Started scraping recetecom")

            try:
                category_urls = self.get_product_category_urls()
                logger.info(f" \t\u2714 Found {len(category_urls)} categories on recetecom")

                for product_category in category_urls:
                    product_urls = self.get_product_urls_from_product_category(product_category)

                    for url in product_urls[:1]:
                        soup = self.scrap_page(url)
                        if soup:
                            raw_data = self.prepare_raw_data(self.get_product_details(soup))
                            self.rabbitmq.publish(body=raw_data)

                logger.info(" \t\u2714 Finished scraping recetecom")
                return


            except Exception as e:
                logger.error(f"Error on recetecom: {e}")

def main(url: str = None):
    scraper = Scraper()
    return scraper.scrape(url=url)