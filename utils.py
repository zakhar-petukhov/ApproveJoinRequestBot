import json
import os
from datetime import datetime, timedelta

import jsonpickle
import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache
from telethon import Button, TelegramClient

import config
from models import User

cache_data = TTLCache(maxsize=50000, ttl=timedelta(minutes=7), timer=datetime.now)

bot = TelegramClient('utils_bot', config.API_ID, config.API_HASH).start(bot_token=config.BOT_TOKEN)


def get_currency(ru=False, uah=False, crypto=False, other=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

    list_currency = []
    if uah:
        urls = {
            "USD": 'https://finance.yahoo.com/quote/USDUAH=X?.tsrc=applewf',
            "EUR": 'https://finance.yahoo.com/quote/EURUAH=X?.tsrc=applewf',
        }

        for key, value in urls.items():
            item = cache_data.get(f"{key}/UAH", None)
            if item is None:
                price, change = parse_body(value, headers)
                if key == "USD":
                    line = f"🇺🇸 USD/UAH **{price}** __{change}__"
                    list_currency.append(line)
                else:
                    line = f"🇪🇺 EUR/UAH **{price}** __{change}__"
                    list_currency.append(line)

                cache_data[f"{key}/UAH"] = line

            else:
                list_currency.append(item)

    elif ru:
        urls = {
            "USD": 'https://finance.yahoo.com/quote/USDRUB=X?.tsrc=applewf',
            "EUR": 'https://finance.yahoo.com/quote/EURRUB=X?.tsrc=applewf',
        }

        for key, value in urls.items():
            item = cache_data.get(f"{key}/RUB", None)
            if item is None:
                price, change = parse_body(value, headers)
                if key == "USD":
                    line = f"🇺🇸 USD/RUB **{price}** __{change}__"
                    list_currency.append(line)
                else:
                    line = f"🇪🇺 EUR/RUB **{price}** __{change}__"
                    list_currency.append(line)

                cache_data[f"{key}/RUB"] = line

            else:
                list_currency.append(item)

    elif other:
        urls = {
            "EUR/USD": 'https://finance.yahoo.com/quote/EURUSD=X?.tsrc=applewf',
            "GBP/USD": 'https://finance.yahoo.com/quote/GBPUSD=X?.tsrc=applewf',
            "CHF/USD": 'https://finance.yahoo.com/quote/CHFUSD=X?.tsrc=applewf',
            "JPY/USD": 'https://finance.yahoo.com/quote/JPYUSD=X?.tsrc=applewf',
            "CNY/USD": 'https://finance.yahoo.com/quote/CNYUSD=X?.tsrc=applewf',
        }

        for key, value in urls.items():
            item = cache_data.get(key, None)
            if item is None:
                price, change = parse_body(value, headers)
                line = ""

                if key == "EUR/USD":
                    line = f"🇪🇺 {key} **{price}** __{change}__"
                    list_currency.append(line)
                elif key == "GBP/USD":
                    line = f"🇬🇧 {key} **{price}** __{change}__"
                    list_currency.append(line)
                elif key == "CHF/USD":
                    line = f"🇨🇭 {key} **{price}** __{change}__"
                    list_currency.append(line)
                elif key == "JPY/USD":
                    line = f"🇯🇵 {key} **{price}** __{change}__"
                    list_currency.append(line)
                elif key == "CNY/USD":
                    line = f"🇨🇳 {key} **{price}** __{change}__"
                    list_currency.append(line)

                cache_data[key] = line

            else:
                list_currency.append(item)

    elif crypto:
        currencies = ["Bitcoin USD", "Ethereum USD", "Dogecoin USD", "Terra USD"]

        for value in currencies:
            item = cache_data.get(value, None)
            if item is None:
                list_currency = []
                break
            else:
                list_currency.append(item)

        if len(list_currency) == 0:
            url = "https://finance.yahoo.com/cryptocurrencies/"
            full_page = requests.get(url, headers=headers)
            soup = BeautifulSoup(full_page.content, 'html.parser')
            blocks = soup.find_all("tr", {
                "class": "simpTblRow"
            })

            for value in blocks:
                title = value.find("td", {"aria-label": "Name"}).text

                if title in currencies:
                    price = value.find("td", {"aria-label": "Price (Intraday)"}).text
                    change = value.find("td", {"aria-label": "% Change"}).text

                    line = f"🔹 {title}: **{price}** __({change})__"
                    cache_data[title] = line
                    list_currency.append(line)

        item = cache_data.get("USDT", None)
        if item is None:
            url = "https://www.bestchange.net/ruble-cash-to-tether-trc20.html"
            full_page = requests.get(url, headers=headers)
            soup = BeautifulSoup(full_page.content, 'html.parser')
            blocks = soup.find_all("div", {
                "class": "fs"
            })
            if len(blocks) > 0:
                price = blocks[0].text.split()[0]
            else:
                price = 0

            item = f"🔹 USDT: **{price}** __(лучший курс, по которому возможно купить)__"
            cache_data["USDT"] = item

        list_currency.append(item)

        other_currencies = ["Solana", "GST", "BNB", "GST_BSC"]
        for value in other_currencies:
            item = cache_data.get(value, None)
            if item is None:
                if value == "Solana":
                    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=USD"
                    request = requests.get(url, headers=headers)
                    response = request.json()
                    solana = response.get("solana")
                    if solana is not None:
                        price = solana["usd"]
                        item = f"🔹 Solana: **{price}** "

                elif value == "GST":
                    url = "https://api.coingecko.com/api/v3/simple/price?ids=green-satoshi-token&vs_currencies=USD"
                    request = requests.get(url, headers=headers)
                    response = request.json()
                    gst = response.get("green-satoshi-token")
                    if gst is not None:
                        price = gst["usd"]
                        item = f"🔹 GST: **{price}** "

                elif value == "BNB":
                    url = "https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=USD"
                    request = requests.get(url, headers=headers)
                    response = request.json()
                    binance_coin = response.get("binancecoin")
                    if binance_coin is not None:
                        price = binance_coin["usd"]
                        item = f"🔹 BNB: **{price}** "

                elif value == "GST_BSC":
                    url = "https://api.coingecko.com/api/v3/simple/price?ids=green-satoshi-token-bsc&vs_currencies=USD"
                    request = requests.get(url, headers=headers)
                    response = request.json()
                    gst_bsc = response.get("green-satoshi-token-bsc")
                    if gst_bsc is not None:
                        price = gst_bsc["usd"]
                        item = f"🔹 GST_BSC: **{price}** "

                cache_data[value] = item
                list_currency.append(item)

            else:
                list_currency.append(item)

    return '\n'.join(list_currency)


def parse_body(url, headers):
    full_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(full_page.content, 'html.parser')
    price = soup.find("fin-streamer", {"data-field": "regularMarketPrice", "data-test": "qsp-price"}).text
    change = soup.find("fin-streamer", {"data-field": "regularMarketChangePercent",
                                        "class": "Fw(500) Pstart(8px) Fz(24px)"}).text

    return price, change


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
        preview = '✅' if data['preview'] != 'False' else '❌'
        content = '✅' if data['content'] != 'False' else '❌'

        if 'video:' in data['media']:
            video = '✅'
            photo = '❌'
        else:
            if 'photo:' in data['media'] or 'animation:' in data['media']:
                video = '❌'
                photo = '✅'
            else:
                video = '❌'
                photo = '❌'

        text = f"""
<i>Сообщение для массовой рассылки:</i>

<b>Текст:</b> 
{text}

<b>Кнопка:</b> 
{button}

<b>Фото или GIF:</b> 
{photo}

<b>Видео:</b> 
{video}

<b>Контент снизу:</b> 
{content}

<b>Предпросмотр:</b> 
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
            await bot.send_message(admin_id, 'Ошибка! Добавьте текст или фото', parse_mode='html')
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

        len_users = len(users)
        mail_sent = 0

        if media == 'None':
            if preview == False:
                for user in users:
                    user_id = user['user_id']

                    try:
                        await bot.send_message(user_id, text, formatting_entities=entities, link_preview=web_preview,
                                               buttons=keyboard)
                        mail_sent += 1

                    except:
                        User.update(active=False).where(User.user_id == user_id).execute()
            else:
                await bot.send_message(admin_id, text, formatting_entities=entities, link_preview=web_preview,
                                       buttons=keyboard)

        else:
            file = media.split(':')[1]

            if 'photo:' in media:
                file = open(file, 'rb')

            if preview == False:
                for user in users:
                    user_id = user['user_id']

                    try:
                        await bot.send_file(user_id, file, formatting_entities=entities, caption=text, buttons=keyboard)
                        mail_sent += 1

                    except:
                        User.update(active=False).where(User.user_id == user_id).execute()
            else:
                await bot.send_file(admin_id, file, formatting_entities=entities, caption=text, buttons=keyboard)

        if preview == False:
            blocked_users = len_users - mail_sent

            await bot.send_message(admin_id,
                                   f'Сообщение было успешно отправлено:\n\nПользователи, получившие сообщение: <b>{mail_sent}</b>\nУдаленные пользователи, которые заблокировали бота: <b>{blocked_users}</b>',
                                   parse_mode='html')

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
        text = '⁠' + text

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
