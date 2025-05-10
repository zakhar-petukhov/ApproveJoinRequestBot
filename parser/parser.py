import logging

import aiohttp
from bs4 import BeautifulSoup

# Basic logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseParser:
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    async def fetch(self, session, url, name, proxy=None):
        try:
            async with session.get(url, proxy=proxy) as response:
                response.raise_for_status()
                return await response.text(), url, name
        except Exception as e:
            logger.error(f"[Fetch] Failed to fetch {name} from {url}: {e}")
            return "", url, name

    async def parse_bestchange(self, name, url: str):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            html, _, _ = await self.fetch(session, url, name)
            if not html:
                return name, "0"
            soup = BeautifulSoup(html, 'html.parser')
            price_block = soup.select_one("div.fs")
            # Find price blocks
            if price_block:
                price = price_block.text.strip().split()[0]
            else:
                price = "0"

            return name, price
