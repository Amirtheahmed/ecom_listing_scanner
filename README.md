# Listing Scanner - Scalable Web Scrapper for E-Commerce Websites

## Overview
Listing Scanner is a scalable Python web scraping project designed for scrapping e-commerce websites. It is capable of efficiently scrapping product details.

## Getting Started
### Usage
- Clone the repository or download the source code.
- Install dependencies with `pip install -r requirements.txt`
- Deploy RabbitMQ server with docker-compose.yml file
  - run `docker-compose up -d`
- copy .env.example to .env and set up environment variables
- run `python3.10 -m src.main --channel <channel>` to scan whole website
- run `python3.10 -m src.main --url <url>` to scan specific product


### Prerequisites
- Docker (for containerized deployment)
- Python 3.x
- Dependencies listed in `requirements.txt`

### Installation
1. Clone the repository or download the source code.
2. Install dependencies using `pip install -r requirements.txt`:
3. Set up environment variables by creating a `.env` file based on the provided template inside `.env.example`.

### Usage
- To start the application, run `main.py` from the `src` directory with `python3.10 -m src.main`.
- The application can also be containerized using Docker. A `Dockerfile` and a `Makefile` are provided for ease of deployment.

## Project Structure

- `Dockerfile` - Instructions for Docker to build the application.
- `Makefile` - Simplifies command execution for building and running the application.
- `src/main.py` - The main script to run the application.
- `src/base_scrapper.py`, `logger.py`, `proxy_manager.py`, - Core modules of the application.
- `src/scrappers/` - Directory containing current scrapper modules.
- `src/rabbitmq.py` - Contains Producer class used to send messages to a RabbitMQ queue.

## Contributing
Please follow the existing coding style and submit pull requests for any new features or bug fixes.

## Contact
For any further queries or issues, please contact the repository maintainer at [amirsalihdev@gmail.com](mailto:amirsalihdev@gmail.com).
