from datetime import datetime

from bs4 import BeautifulSoup
from bot.cache import cache_data
from bot.parser import BaseParser
from db.models import User, Price

FLAGS = {
    "USD/UAH": "🇺🇸",
    "EUR/UAH": "🇪🇺",
    "USD/RUB": "🇺🇸",
    "EUR/RUB": "🇪🇺",
    "TRY/RUB": "🇹🇷",
    "GEL/RUB": "🇬🇪",
    "KZT/RUB": "🇰🇿",
    "AMD/RUB": "🇦🇲",
    "BYN/RUB": "🇧🇾",
    "AZN/RUB": "🇦🇿",
    "CNY/RUB": "🇨🇳",
    "EUR/USD": "🇪🇺",
    "GBP/USD": "🇬🇧",
    "CHF/USD": "🇨🇭",
    "JPY/USD": "🇯🇵",
    "CNY/USD": "🇨🇳"

}


async def get_currency(ru=False, uah=False, crypto=False, other=False):
    parse = BaseParser()

    list_currency = []

    if uah:
        urls = {
            "USD/UAH": 'https://query1.finance.yahoo.com/v8/finance/chart/USDUAH=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "EUR/UAH": 'https://query1.finance.yahoo.com/v8/finance/chart/EURUAH=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
        }

        for name, url in urls.items():
            item = cache_data.get(f"{name}/UAH", None)
            if item is None:
                _, price, change = parse.parse_yahoo(name, url)

                flag = FLAGS.get(name, None)
                if flag is not None:
                    line = f"{flag} {name} **{price}** __{change}__"
                    list_currency.append(line)
                    cache_data[name] = line

            else:
                list_currency.append(item)

    elif ru:
        urls = {
            "USD/RUB": 'https://ru.investing.com/currencies/usd-rub',
            "EUR/RUB": 'https://ru.investing.com/currencies/eur-rub',
            "TRY/RUB": 'https://ru.investing.com/currencies/try-rub',
            "GEL/RUB": 'https://ru.investing.com/currencies/gel-rub',
            "KZT/RUB": 'https://ru.investing.com/currencies/kzt-rub',
            "AMD/RUB": 'https://ru.investing.com/currencies/amdrubfix=',
            "BYN/RUB": 'https://ru.investing.com/currencies/byn-rub',
            "AZN/RUB": 'https://ru.investing.com/currencies/azn-rub',
            "CNY/RUB": 'https://ru.investing.com/currencies/cny-rub',
        }

        cache_data["send_msg/rus"] = True

        htmls, list_currency = await parse.get_htmls_and_cache_data(urls)
        for html in htmls:
            name = html[2]

            soup = BeautifulSoup(html[0], 'html.parser')
            price = soup.find("span", {"data-test": "instrument-price-last"})
            if price is not None:
                price = price.text.replace(",", ".")
            else:
                price = 0

            percent = soup.find("span", {"data-test": "instrument-price-change-percent"})
            if percent is not None:
                change = percent.text.replace(",", ".")
            else:
                change = 0

            flag = FLAGS.get(name, None)
            if flag is not None:
                line = f"{flag} {name} **{price}** __{change}__"
                list_currency.append(line)
                cache_data[name] = line

    elif other:
        urls = {
            "EUR/USD": 'https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "GBP/USD": 'https://query1.finance.yahoo.com/v8/finance/chart/GBPUSD=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "CHF/USD": 'https://query1.finance.yahoo.com/v8/finance/chart/CHFUSD=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "JPY/USD": 'https://query1.finance.yahoo.com/v8/finance/chart/JPYUSD=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "CNY/USD": 'https://query1.finance.yahoo.com/v8/finance/chart/CNYUSD=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
        }

        for name, url in urls.items():
            item = cache_data.get(name, None)
            if item is None:
                _, price, change = parse.parse_yahoo(name, url)

                flag = FLAGS.get(name, None)
                if flag is not None:
                    line = f"{flag} {name} **{price}** __{change}__"
                    list_currency.append(line)
                    cache_data[name] = line

            else:
                list_currency.append(item)

    elif crypto:
        urls = {
            "Bitcoin USD": 'https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "Ethereum USD": 'https://query1.finance.yahoo.com/v8/finance/chart/ETH-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "USDT": 'https://www.bestchange.net/ruble-cash-to-tether-trc20.html',
            "Litecoin USD": 'https://query1.finance.yahoo.com/v8/finance/chart/LTC-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "XRP USD": 'https://query1.finance.yahoo.com/v8/finance/chart/XRP-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "Dogecoin USD": 'https://query1.finance.yahoo.com/v8/finance/chart/DOGE-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "GMT": 'https://query1.finance.yahoo.com/v8/finance/chart/GMT3-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "Solana": 'https://query1.finance.yahoo.com/v8/finance/chart/SOL-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "TON": 'https://query1.finance.yahoo.com/v8/finance/chart/TONCOIN-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "GST": 'https://query1.finance.yahoo.com/v8/finance/chart/GST2-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "BNB": 'https://query1.finance.yahoo.com/v8/finance/chart/BNB-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "GST_BSC": 'https://query1.finance.yahoo.com/v8/finance/chart/GST3-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
        }

        for name, url in urls.items():
            item = cache_data.get(name, None)
            if item is None or "Нет данных" in item:
                cache_data["send_msg/crypto"] = True
                change = 0

                if name == "USDT":
                    name, price = await parse.parse_bestchange(name, url)
                else:
                    name, price, change = parse.parse_yahoo(name, url)

                if price == -100 or change == -100:
                    value = Price.select().where(Price.name == name).dicts()
                    if value.exists():
                        value = value[0]
                        price = value["price"]
                        change = value["change"]

                    else:
                        price = "Нет данных о цене"
                        change = "Нет данных об изменении"

                else:
                    price_value = Price.get_or_none(name=name)
                    if price_value is None:
                        Price.create(name=name, price=price, change=change)
                    else:
                        Price.update(price=price, change=change).where(Price.name == name).execute()

                if name == "USDT":
                    line = f"🔸 USDT: **{price}** __(лучший курс, по которому возможно купить)__"

                elif name == "Ethereum USD":
                    line = f"🔸 {name} **{price}** __{change}__"

                elif name == "Bitcoin USD":
                    line = f"🔸 {name} **{price}** __{change}__"

                else:
                    line = f"🔹 {name} **{price}** __{change}__"

                cache_data[name] = line
                list_currency.append(line)

            else:
                list_currency.append(item)

    return '\n'.join(list_currency) + '\n\nАктуальные курсы: @bestchangenanbot'


def get_or_create_user(who):
    user = User.get_or_none(user_id=who)
    if user is None:
        user = User.create(user_id=who)

    if not user.active:
        user.active = True
        user.save()


def time_until_end_of_day(dt=None):
    if dt is None:
        dt = datetime.now()
    return ((24 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second)
