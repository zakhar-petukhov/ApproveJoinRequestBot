import asyncio
import platform

import aiohttp
from bs4 import BeautifulSoup
from seleniumwire import webdriver
import requests

from bot.cache import cache_data


class BaseParser:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) \
Version/15.4 Safari/605.1.15'
    }
    driver = None

    def __init__(self):
        my_os = platform.system()
        self.driver_path = r"drivers/chromedriver_linux"
        if my_os == "Darwin":
            self.driver_path = r"drivers/chromedriver_mac"

    def get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        if self.driver is None:
            self.driver = webdriver.Chrome(executable_path=self.driver_path, options=options)

        return self.driver

    def parse_yahoo(self, name, url: str):
        try:
            request = requests.get(url, headers=self.headers)
            data = request.json()

            chart_previous_close = round(data['chart']['result'][0]['meta']['chartPreviousClose'], 4)
            regular_market_price = round(data['chart']['result'][0]['meta']['regularMarketPrice'], 4)
            percent = round((regular_market_price / chart_previous_close - 1) * 100, 2)

        except:
            return name, -100, -100

        return name, regular_market_price, f"({f'+{percent}' if percent > 0 else percent}%)"

    def parse_coingecko(self, name, url: str):
        try:
            request = requests.get(url, headers=self.headers)
            data = request.json()
            regular_market_price = round(data['the-open-network']['usd'], 4)

        except:
            return name, -100

        return name, regular_market_price

    async def fetch(self, session, url, name):
        try:
            async with session.get(url) as response:
                text = await response.text()
                return text, url, name
        except Exception as e:
            print(str(e))

    async def parse_bestchange(self, name, url: str):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            html, _, _ = await self.fetch(session, url, name)
            soup = BeautifulSoup(html, 'html.parser')

            blocks = soup.find_all("div", {
                "class": "fs"
            })
            if len(blocks) > 0:
                price = blocks[0].text.split()[0]
            else:
                price = 0

            return name, price

    async def get_htmls_and_cache_data(self, urls):
        parse_tasks = []
        need_htmls = []
        currency_from_cache = []

        async with aiohttp.ClientSession(headers=self.headers) as session:
            for name, url in urls.items():
                item = cache_data.get(name, None)
                if item is None:
                    parse_tasks.append(self.fetch(session, url, name))

                else:
                    currency_from_cache.append(item)

            need_htmls.extend(await asyncio.gather(*parse_tasks))

            return need_htmls, currency_from_cache
