import aiohttp
import asyncio
import logging
from datetime import datetime
from parser.parser import BaseParser
from db.models import Price
import json

logger = logging.getLogger(__name__)


class DataUpdater:
    def __init__(self, update_interval_seconds=300, sleep_time=1):
        # Initialize the updater with the specified interval and parser
        self.update_interval = update_interval_seconds
        self.sleep_time = sleep_time  # Time to sleep between requests
        self.parser = BaseParser()
        self.running = False
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/123.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }

    async def start(self):
        # Start the update process with the specified interval
        self.running = True
        while self.running:
            try:
                await self.update_all_data()
                logger.info(f"Data successfully updated: {datetime.now()}")
            except Exception as e:
                logger.error(f"Error during data update: {e}")
            await asyncio.sleep(self.update_interval)

    def stop(self):
        # Stop the update process
        self.running = False
        logger.info("Data update stopped")

    async def update_all_data(self):
        # Update both fiat and crypto data
        await asyncio.gather(
            self.update_fiat(),
            self.update_crypto_data()
        )

    async def fetch_data(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    text = await response.text()
                    return json.loads(text)
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching data from {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {url}: {e}")
            return None

    async def update_fiat(self):
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        data = await self.fetch_data(url)
        if not data:
            return

        # Process RUB and other pairs
        await self.update_rub_pairs(data)
        await self.update_cross_rates(data)

    async def update_rub_pairs(self, data):
        rub_pairs = {
            "USD": "USD/RUB",
            "EUR": "EUR/RUB",
            "TRY": "TRY/RUB",
            "GEL": "GEL/RUB",
            "KZT": "KZT/RUB",
            "AMD": "AMD/RUB",
            "BYN": "BYN/RUB",
            "AZN": "AZN/RUB",
            "CNY": "CNY/RUB"
        }

        for code, display_name in rub_pairs.items():
            await self.update_pair_price(data, code, display_name)

    async def update_cross_rates(self, data):
        # USD/UAH and EUR/UAH calculation
        await self.calculate_cross_rate(data, "USD", "UAH", "USD/UAH")
        await self.calculate_cross_rate(data, "EUR", "UAH", "EUR/UAH")

        # Other currency pairs (previously fetched from Yahoo)
        other_pairs = {
            "EUR/USD": ("EUR", "USD"),
            "GBP/USD": ("GBP", "USD"),
            "CHF/USD": ("CHF", "USD"),
            "JPY/USD": ("JPY", "USD"),
            "CNY/USD": ("CNY", "USD")
        }

        for pair_name, (base, quote) in other_pairs.items():
            await self.update_cross_currency_pair(data, base, quote, pair_name)

    async def update_pair_price(self, data, code, display_name):
        try:
            value = data["Valute"].get(code)
            if not value:
                return
            price = value["Value"]
            previous = value["Previous"]
            change = round(((price - previous) / previous) * 100, 2)
            change_str = f"({f'+{change}' if change > 0 else change}%)"
            await self.update_price_in_db(display_name, price, change_str)
        except Exception as e:
            logger.error(f"Error updating {display_name}: {e}")

    async def calculate_cross_rate(self, data, base_code, quote_code, pair_name):
        try:
            base_rub = self.get_rub_rate(data, base_code)
            quote_rub = self.get_rub_rate(data, quote_code)
            price = base_rub / quote_rub

            base_prev = self.get_previous_rate(data, base_code)
            quote_prev = self.get_previous_rate(data, quote_code)
            previous_price = base_prev / quote_prev

            change = round(((price - previous_price) / previous_price) * 100, 2)
            change_str = f"({f'+{change}' if change > 0 else change}%)"
            await self.update_price_in_db(pair_name, price, change_str)
        except Exception as e:
            logger.error(f"Error calculating cross rate for {pair_name}: {e}")

    def get_rub_rate(self, data, currency_code):
        value = data["Valute"].get(currency_code)
        if value:
            return value["Value"] / value["Nominal"]
        return 0

    def get_previous_rate(self, data, currency_code):
        value = data["Valute"].get(currency_code)
        if value:
            return value["Previous"] / value["Nominal"]
        return 0

    async def update_cross_currency_pair(self, data, base, quote, pair_name):
        try:
            base_rub = self.get_rub_rate(data, base)
            quote_rub = self.get_rub_rate(data, quote)
            price = base_rub / quote_rub

            base_prev = self.get_previous_rate(data, base)
            quote_prev = self.get_previous_rate(data, quote)
            previous_price = base_prev / quote_prev

            change = round(((price - previous_price) / previous_price) * 100, 2)
            change_str = f"({f'+{change}' if change > 0 else change}%)"
            await self.update_price_in_db(pair_name, price, change_str)
        except Exception as e:
            logger.error(f"Error updating {pair_name}: {e}")

    async def update_crypto_data(self):
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,litecoin,ripple,dogecoin,solana,the-open-network,binancecoin&vs_currencies=USD"
        data = await self.fetch_data(url)
        if not data:
            return

        crypto_mapping = {
            "bitcoin": "Bitcoin USD",
            "ethereum": "Ethereum USD",
            "litecoin": "Litecoin USD",
            "ripple": "XRP USD",
            "dogecoin": "Dogecoin USD",
            "solana": "Solana",
            "the-open-network": "TON",
            "binancecoin": "BNB"
        }

        for gecko_id, display_name in crypto_mapping.items():
            await self.process_crypto_data(data, gecko_id, display_name)

        # Handle USDT separately using BestChange
        try:
            usdt_url = 'https://www.bestchange.net/ruble-cash-to-tether-trc20.html'
            name, price = await self.parser.parse_bestchange("USDT", usdt_url)
            await self.update_price_in_db(name, price, "")
        except Exception as e:
            logger.error(f"Error updating USDT: {e}")

    async def process_crypto_data(self, data, gecko_id, display_name):
        try:
            if gecko_id in data and "usd" in data[gecko_id]:
                price = data[gecko_id]["usd"]
                await self.update_price_in_db(display_name, price, "")
            else:
                logger.warning(f"No data found for {gecko_id} in CoinGecko response")
        except Exception as e:
            logger.error(f"Error processing {display_name} data: {e}")

    async def update_price_in_db(self, name, price, change=""):
        try:
            now = datetime.now()
            Price.insert(
                name=name,
                price=price,
                change=change,
                date_update=now
            ).on_conflict(
                conflict_target=[Price.name],
                update={
                    Price.price: price,
                    Price.change: change,
                    Price.date_update: now
                }
            ).execute()
        except Exception as e:
            logger.error(f"Error saving {name} to database: {e}")
