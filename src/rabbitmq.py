# rabbitmq.py
import json
import uuid
import logging
from os import getenv
import pika
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Constants for queue names and other configurations
QUEUE_NAME = 'listings'
ROUTING_KEY = 'v1'
EXCHANGE_NAME = 'amq.direct'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RabbitMQ:
    """Producer class to send messages to a message queue."""

    def __init__(self):
        """Initialize the producer with a connection to RabbitMQ."""
        try:
            parameters = pika.ConnectionParameters(
                host=getenv('RABBITMQ_HOST'),
                port=int(getenv('RABBITMQ_PORT')),
                virtual_host='/',
                credentials=pika.PlainCredentials(getenv('RABBITMQ_USER'), getenv('RABBITMQ_PASS'))
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=QUEUE_NAME, durable=True)
            logging.info("RabbitMQ initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize RabbitMQ: {e}")
            raise

    def __enter__(self):
        """Enter method for context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit method for context manager protocol to ensure resources are cleaned up."""
        self.channel.close()
        self.connection.close()
        if exc_type:
            logging.error(f"An error occurred: {exc_value}")
        logging.info("RabbitMQ connection closed.")

    def publish(self, body, headers=None):
        """Publish a message to the queue."""
        if headers is None:
            headers = {}
        try:
            job_id = str(uuid.uuid4())
            self.channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=ROUTING_KEY,
                body=json.dumps(body).encode('utf-8'),
                properties=pika.BasicProperties(headers={'job_id': job_id, **headers})
            )
            logging.info(f"Published message to queue: {job_id}")
        except Exception as e:
            logging.error(f"Failed to publish message: {e}")
            raise
