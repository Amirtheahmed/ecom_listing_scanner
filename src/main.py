import argparse
import asyncio
from importlib import import_module

import pika
from os import environ as env
from dotenv import load_dotenv
from src.logger import setup_logger
from src.proxy_manager import ProxyManager

def setup_rabbitmq_connection():
    """Setup RabbitMQ connection parameters and return them."""
    parameters = pika.ConnectionParameters(
        host=env['RABBITMQ_HOST'],
        port=int(env['RABBITMQ_PORT']),
        virtual_host='/',
        credentials=pika.PlainCredentials(env['RABBITMQ_USER'], env['RABBITMQ_PASS'])
    )
    return parameters

def init(channel_name: str, link: str = None):
    try:
        scrapper_module_name = f".{channel_name.lower()}_scrapper"
        scrapper_module = import_module(scrapper_module_name, package='src.scrappers')

        if callable(getattr(scrapper_module, 'main', None)):
            if link:
                asyncio.run(scrapper_module.main(url=link))
            else:
                asyncio.run(scrapper_module.main())
        else:
            logger.error(f"Scrapper module for '{channel_name}' does not have a 'scrape' function.")
            return False

    except ModuleNotFoundError:
        logger.error(f"Scrapper module for '{channel_name}' not found.")
        return False
    except Exception as e:
        logger.error(f"An error occurred in the scrapper module for '{channel_name}': {e}")
        return False


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel', type=str, required=True)
    parser.add_argument('--url', type=str)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    load_dotenv()
    logger = setup_logger()
    proxy_manager = ProxyManager()

    args = get_args()
    channel = args.channel
    product_url = args.url

    init(channel_name=channel, link=product_url)


