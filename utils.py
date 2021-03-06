import json
import os
import time
from datetime import datetime, timedelta

import asyncio
import jsonpickle
import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache
from telethon import Button, TelegramClient

import config
from models import User, Price

cache_data = TTLCache(maxsize=50000, ttl=timedelta(minutes=7), timer=datetime.now)

bot = TelegramClient('utils_bot', config.API_ID, config.API_HASH).start(bot_token=config.BOT_TOKEN)


def get_currency(ru=False, uah=False, crypto=False, other=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'}

    list_currency = []
    if uah:
        urls = {
            "USD": 'https://query1.finance.yahoo.com/v8/finance/chart/USDUAH=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "EUR": 'https://query1.finance.yahoo.com/v8/finance/chart/EURUAH=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
        }

        for name, url in urls.items():
            item = cache_data.get(f"{name}/UAH", None)
            if item is None:
                _, price, change = parse_body(url, name, headers)
                if name == "USD":
                    line = f"πΊπΈ USD/UAH **{price}** __{change}__"
                    list_currency.append(line)
                else:
                    line = f"πͺπΊ EUR/UAH **{price}** __{change}__"
                    list_currency.append(line)

                cache_data[f"{name}/UAH"] = line

            else:
                list_currency.append(item)

    elif ru:
        urls = {
            "USD": 'https://query1.finance.yahoo.com/v8/finance/chart/USDRUB=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "EUR": 'https://query1.finance.yahoo.com/v8/finance/chart/EURRUB=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "TRY": 'https://query1.finance.yahoo.com/v8/finance/chart/TRYRUB.ME?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
        }

        for name, url in urls.items():
            item = cache_data.get(f"{name}/RUB", None)
            if item is None:
                _, price, change = parse_body(url, name, headers)
                if name == "USD":
                    line = f"πΊπΈ USD/RUB **{price}** __{change}__"
                    list_currency.append(line)

                elif name == "TRY":
                    line = f"πΉπ· TRY/RUB **{price}** __{change}__"
                    list_currency.append(line)

                else:
                    line = f"πͺπΊ EUR/RUB **{price}** __{change}__"
                    list_currency.append(line)

                cache_data[f"{name}/RUB"] = line

            else:
                list_currency.append(item)

    elif other:
        urls = {
            "EUR/USD": 'https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "GBP/USD": 'https://query1.finance.yahoo.com/v8/finance/chart/GBPUSD=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "CHF/USD": 'https://query1.finance.yahoo.com/v8/finance/chart/CHFUSD=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "JPY/USD": 'https://query1.finance.yahoo.com/v8/finance/chart/JPYUSD=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "CNY/USD": 'https://query1.finance.yahoo.com/v8/finance/chart/CNYUSD=X?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
        }

        for name, url in urls.items():
            item = cache_data.get(url, None)
            if item is None:
                _, price, change = parse_body(url, name, headers)
                line = ""

                if name == "EUR/USD":
                    line = f"πͺπΊ {name} **{price}** __{change}__"
                    list_currency.append(line)
                elif name == "GBP/USD":
                    line = f"π¬π§ {name} **{price}** __{change}__"
                    list_currency.append(line)
                elif name == "CHF/USD":
                    line = f"π¨π­ {name} **{price}** __{change}__"
                    list_currency.append(line)
                elif name == "JPY/USD":
                    line = f"π―π΅ {name} **{price}** __{change}__"
                    list_currency.append(line)
                elif name == "CNY/USD":
                    line = f"π¨π³ {name} **{price}** __{change}__"
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
            "GST": 'https://query1.finance.yahoo.com/v8/finance/chart/GST2-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "BNB": 'https://query1.finance.yahoo.com/v8/finance/chart/BNB-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
            "GST_BSC": 'https://query1.finance.yahoo.com/v8/finance/chart/GST3-USD?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance',
        }

        for name, url in urls.items():
            item = cache_data.get(name, None)
            if item is None or "ΠΠ΅Ρ Π΄Π°Π½Π½ΡΡ" in item:
                cache_data["send_msg"] = True
                if name == "USDT":
                    name, price, change = parse_body_USDT(url, name, headers)
                else:
                    name, price, change = parse_body(url, name, headers)

                if price == -100 or change == -100:
                    value = Price.select().where(Price.name == name).dicts()
                    if value.exists():
                        value = value[0]
                        price = value["price"]
                        change = value["change"]

                    else:
                        price = "ΠΠ΅Ρ Π΄Π°Π½Π½ΡΡ ΠΎ ΡΠ΅Π½Π΅"
                        change = "ΠΠ΅Ρ Π΄Π°Π½Π½ΡΡ ΠΎΠ± ΠΈΠ·ΠΌΠ΅Π½Π΅Π½ΠΈΠΈ"
                else:
                    price_value = Price.get_or_none(name=name)
                    if price_value is None:
                        Price.create(name=name, price=price, change=change)
                    else:
                        Price.update(price=price, change=change).where(Price.name == name).execute()

                if name == "USDT":
                    line = f"πΉ USDT: **{price}** __(Π»ΡΡΡΠΈΠΉ ΠΊΡΡΡ, ΠΏΠΎ ΠΊΠΎΡΠΎΡΠΎΠΌΡ Π²ΠΎΠ·ΠΌΠΎΠΆΠ½ΠΎ ΠΊΡΠΏΠΈΡΡ)__"
                else:
                    line = f"πΉ {name} **{price}** __{change}__"

                cache_data[name] = line
                list_currency.append(line)

            else:
                list_currency.append(item)

    return '\n'.join(list_currency) + '\n\nΠΠΊΡΡΠ°Π»ΡΠ½ΡΠ΅ ΠΊΡΡΡΡ: @bestchangenanbot'


def parse_body_USDT(url, name, headers):
    full_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(full_page.content, 'html.parser')
    blocks = soup.find_all("div", {
        "class": "fs"
    })
    if len(blocks) > 0:
        price = blocks[0].text.split()[0]
    else:
        price = 0

    return name, price, 0


def parse_body(url, name, headers):
    request = requests.get(url, headers=headers)
    data = request.json()

    try:
        chart_previous_close = round(data['chart']['result'][0]['meta']['chartPreviousClose'], 4)
        regular_market_price = round(data['chart']['result'][0]['meta']['regularMarketPrice'], 4)
        percent = round((regular_market_price / chart_previous_close - 1) * 100, 2)
    except:
        return name, -100, -100

    return name, regular_market_price, f"({f'+{percent}' if percent > 0 else percent}%)"


def get_or_create_user(who):
    user = User.get_or_none(user_id=who)
    if user is None:
        user = User.create(user_id=who)

    if not user.active:
        user.active = True
        user.save()


class Setting:
    """Settings class for admin panel"""

    def get_json(self, name):
        """Get or create JSON settings file"""

        try:
            file = open(name, 'r')
            data = json.load(file)

        except FileNotFoundError:
            if name == 'mail.json':
                data = {'text': 'None', 'media': 'None', 'content': 'None', 'button': 'None', 'preview': 'False',
                        'entities': 'None'}

            file = open(name, 'w')
            file.write(json.dumps(data, indent=4, ensure_ascii=False))

        return data

    def change_value(self, name, key, value):
        """Change value of JSON file"""

        data = self.get_json(name)
        data[key] = value
        file = open(name, 'w')
        file.write(json.dumps(data, indent=4, ensure_ascii=False))

    def mail_text(self):
        """Text for admin mail info"""

        data = self.get_json('mail.json')
        text = data['text'] if data['text'] != 'None' else '-'
        button = data['button'] if data['button'] != 'None' else '-'
        preview = 'β' if data['preview'] != 'False' else 'β'
        content = 'β' if data['content'] != 'False' else 'β'

        if 'video:' in data['media']:
            video = 'β'
            photo = 'β'
        else:
            if 'photo:' in data['media'] or 'animation:' in data['media']:
                video = 'β'
                photo = 'β'
            else:
                video = 'β'
                photo = 'β'

        text = f"""
<i>Π‘ΠΎΠΎΠ±ΡΠ΅Π½ΠΈΠ΅ Π΄Π»Ρ ΠΌΠ°ΡΡΠΎΠ²ΠΎΠΉ ΡΠ°ΡΡΡΠ»ΠΊΠΈ:</i>

<b>Π’Π΅ΠΊΡΡ:</b> 
{text}

<b>ΠΠ½ΠΎΠΏΠΊΠ°:</b> 
{button}

<b>Π€ΠΎΡΠΎ ΠΈΠ»ΠΈ GIF:</b> 
{photo}

<b>ΠΠΈΠ΄Π΅ΠΎ:</b> 
{video}

<b>ΠΠΎΠ½ΡΠ΅Π½Ρ ΡΠ½ΠΈΠ·Ρ:</b> 
{content}

<b>ΠΡΠ΅Π΄ΠΏΡΠΎΡΠΌΠΎΡΡ:</b> 
{preview}
"""
        return text

    def switch_preview(self):
        """Mail preview On/Off"""

        data = self.get_json('mail.json')

        if data['preview'] == 'False':
            self.change_value('mail.json', 'preview', 'True')

        elif data['preview'] == 'True':
            self.change_value('mail.json', 'preview', 'False')

    def clear_mail(self):
        """Mail clear"""

        self.change_value('mail.json', 'text', 'None')
        self.change_value('mail.json', 'media', 'None')
        self.change_value('mail.json', 'content', 'False')
        self.change_value('mail.json', 'button', 'None')
        self.change_value('mail.json', 'preview', 'False')
        self.change_value('mail.json', 'entities', 'None')

    async def send_mail(self, preview=False, admin_id=None):
        """Send mail"""

        users = list(User.select().where(User.active != False).dicts())
        data = self.get_json('mail.json')
        text = data['text']
        entities = data['entities']
        media = data['media']
        button = data['button']
        web_preview = data['preview']

        if entities == 'None':
            entities = None
        else:
            entities = jsonpickle.decode(entities)

        if text == 'None' and media == 'None':
            await bot.send_message(admin_id, 'ΠΡΠΈΠ±ΠΊΠ°! ΠΠΎΠ±Π°Π²ΡΡΠ΅ ΡΠ΅ΠΊΡΡ ΠΈΠ»ΠΈ ΡΠΎΡΠΎ', parse_mode='html')
            return

        if text == 'None':
            text = None

        if web_preview == 'False':
            web_preview = False
        else:
            web_preview = True

        if button != 'None':
            name = button.split('|')[0:-1]
            name = ' '.join(name)
            url = button.split('|')[-1]

            keyboard = [
                [
                    Button.url(name, url),
                ]
            ]

        else:
            keyboard = None

        if media == 'None':
            if preview is False:
                await send_async_send_message(users, text, entities, web_preview, keyboard, None)
            else:
                await bot.send_message(admin_id, text, formatting_entities=entities, link_preview=web_preview,
                                       buttons=keyboard)

        else:
            path = media.split(':')[1]
            if 'photo:' not in media:
                if preview is False:
                    await send_async_send_message(users, text, entities, web_preview, keyboard, path)
                else:
                    await bot.send_file(admin_id, path, formatting_entities=entities, caption=text,
                                        buttons=keyboard)

            else:
                with open(path, 'rb') as f:
                    file = f.read()

                    if preview is False:
                        await send_async_send_message(users, text, entities, web_preview, keyboard, file)
                    else:
                        await bot.send_file(admin_id, file, formatting_entities=entities, caption=text,
                                            buttons=keyboard)

    async def download_file(self, file_id):
        """Download file from Telegram server"""

        file_name = await bot.download_media(file_id)
        file = open(file_name, 'rb')

        main_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(main_path, file_name)
        os.remove(path)

        return file

    async def upload_telegraph(self, file_id, content_type):
        """Upload file to Telegraph"""

        file = await self.download_file(file_id)

        contents = {'photo': 'image/jpg', 'animation': 'image/gif', 'video': 'video/mp4'}
        content = contents[content_type]

        data = requests.post('https://telegra.ph/upload', files={'file': ('file', file, content)}).json()
        url = "https://telegra.ph" + data[0]['src']
        file.close()

        return url

    def load_entities(self):
        """Load entities from mail.json"""

        data = self.get_json('mail.json')
        entities = data['entities']

        if entities != 'None':
            entities_data = json.loads(entities)
        else:
            entities_data = []

        return entities_data

    def save_entities(self, entities):
        """Save entities to mail.json"""

        entities = str(entities).replace("'", '\"')
        entities = str(entities).replace("None", 'null')

        self.change_value('mail.json', 'entities', str(entities))

    def add_offset(self):
        """Add offset to all formating in mail.json"""

        entities = self.load_entities()

        for e in entities:
            e['offset'] += 1

        self.save_entities(entities)

    def add_url(self, url):
        """Add url content mail.json"""

        entities = self.load_entities()
        entities.append({'py/object': 'telethon.tl.types.MessageEntityTextUrl', 'offset': 0, 'length': 1, 'url': url})

        self.save_entities(entities)

    def change_url(self, url):
        """Change url content mail.json"""

        entities = self.load_entities()

        entities[-1]['url'] = url

        self.save_entities(entities)

    def add_wordjoiner(self):
        """Add wordjoiner to text mail.json"""

        data = self.get_json('mail.json')
        text = data['text']
        text = 'β ' + text

        self.change_value('mail.json', 'text', text)

    async def add_content(self, file_id, content_type):
        """Add content to mail.json"""

        url = await self.upload_telegraph(file_id, content_type)
        data = self.get_json('mail.json')

        if data['content'] == 'False':
            self.add_offset()
            self.add_wordjoiner()
            self.change_value('mail.json', 'content', 'True')
            self.add_url(url)
        else:
            self.change_url(url)


async def send_async_send_message(users, text, entities, web_preview, keyboard, file):
    tasks = []
    count = 0

    for user in users:
        user_id = user["user_id"]
        tasks.append(send_or_update_active(user_id, text, entities, web_preview, keyboard, file))
        count += 1
        if count > 28:
            time.sleep(1)
            count = 0
            await asyncio.gather(*tasks)
            tasks = []

    if len(users) < 28:
        await asyncio.gather(*tasks)


async def send_or_update_active(user_id, text, entities, web_preview, keyboard, file):
    try:
        if file is not None:
            await bot.send_file(user_id, file, formatting_entities=entities, caption=text,
                                buttons=keyboard,
                                allow_cache=False)
        else:
            await bot.send_message(user_id, text, formatting_entities=entities, link_preview=web_preview,
                                   buttons=keyboard)
    except:
        User.update(active=False).where(User.user_id == user_id).execute()
