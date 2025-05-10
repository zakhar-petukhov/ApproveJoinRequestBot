from db.models import User, Price
from cachetools import TTLCache

# In-memory cache with TTL (time-to-live) of 5 minutes
cache = TTLCache(maxsize=100, ttl=300)

# Flags dictionary to map currency pairs to their respective flags
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

CRYPTO_SYMBOLS = {
    "Bitcoin USD": "🔸",
    "Ethereum USD": "🔸",
    "USDT": "🔸",
    "Litecoin USD": "🔹",
    "XRP USD": "🔹",
    "Dogecoin USD": "🔹",
    "Solana": "🔹",
    "TON": "🔹",
    "BNB": "🔹",
}


async def get_rate(key: str, is_crypto: bool):
    # Check if the key is in the cache first
    if key in cache:
        return cache[key]

    # Fetch from the database if not in cache
    price_data = Price.get_or_none(name=key)
    if price_data:
        price = price_data.price
        change = price_data.change
        flag = FLAGS.get(key, None)

        # For cryptocurrency, don't include change if it's empty, except for USDT
        if is_crypto:
            if key == "USDT":
                result = f"{CRYPTO_SYMBOLS.get(key, '')} {key} **{round(price, 2)}** __(лучший курс, по которому возможно купить)__"
            elif not change:
                result = f"{CRYPTO_SYMBOLS.get(key, '')} {key} **{round(price, 2)}**"
            else:
                result = f"{CRYPTO_SYMBOLS.get(key, '')} {key} **{round(price, 2)}** __{change}__"
        elif flag:
            result = f"{flag} {key} **{round(price, 2)}** __{change}__"
        else:
            result = f"{key} **{round(price, 2)}** __{change}__"

        # Cache the result for 5 minutes
        cache[key] = result
        return result
    else:
        return f"{key} - данные обновляются"


async def get_currency(ru=False, uah=False, crypto=False, other=False):
    list_currency = []

    if uah:
        # Fetch for specific pairs for UAH
        for name in ["USD/UAH", "EUR/UAH"]:
            list_currency.append(await get_rate(name, is_crypto=False))

    elif ru:
        # Fetch for RUB
        fiat_symbols = ["USD", "EUR", "TRY", "GEL", "KZT", "AMD", "BYN", "AZN", "CNY"]
        for name in fiat_symbols:
            symbol = {
                "USD": "USD/RUB", "EUR": "EUR/RUB", "TRY": "TRY/RUB",
                "GEL": "GEL/RUB", "KZT": "KZT/RUB", "AMD": "AMD/RUB",
                "BYN": "BYN/RUB", "AZN": "AZN/RUB", "CNY": "CNY/RUB"
            }.get(name)
            list_currency.append(await get_rate(symbol, is_crypto=False))

    elif other:
        # Fetch for other USD pairs
        currencies = ["EUR/USD", "GBP/USD", "CHF/USD", "JPY/USD", "CNY/USD"]
        for name in currencies:
            list_currency.append(await get_rate(name, is_crypto=False))

    elif crypto:
        # Fetch for cryptocurrencies
        crypto_currencies = [
            "Bitcoin USD", "Ethereum USD", "USDT", "Litecoin USD",
            "XRP USD", "Dogecoin USD", "Solana", "TON", "BNB"
        ]
        for name in crypto_currencies:
            list_currency.append(await get_rate(name, is_crypto=True))

    return '\n'.join(list_currency) + '\n\nАктуальные курсы: @bestchangenanbot'


def get_or_create_user(who):
    user = User.get_or_none(user_id=who)
    if user is None:
        user = User.create(user_id=who)

    if not user.active:
        user.active = True
        user.save()
