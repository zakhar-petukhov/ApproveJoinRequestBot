import json
import os
from datetime import datetime, timedelta
from multiprocessing.pool import ThreadPool

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

        for name, url in urls.items():
            item = cache_data.get(f"{name}/UAH", None)
            if item is None:
                _, price, change = parse_body(url, name, headers)
                if name == "USD":
                    line = f"🇺🇸 USD/UAH **{price}** __{change}__"
                    list_currency.append(line)
                else:
                    line = f"🇪🇺 EUR/UAH **{price}** __{change}__"
                    list_currency.append(line)

                cache_data[f"{name}/UAH"] = line

            else:
                list_currency.append(item)

    elif ru:
        urls = {
            "USD": 'https://finance.yahoo.com/quote/USDRUB=X?.tsrc=applewf',
            "EUR": 'https://finance.yahoo.com/quote/EURRUB=X?.tsrc=applewf',
        }

        for name, url in urls.items():
            item = cache_data.get(f"{name}/RUB", None)
            if item is None:
                _, price, change = parse_body(url, name, headers)
                if name == "USD":
                    line = f"🇺🇸 USD/RUB **{price}** __{change}__"
                    list_currency.append(line)
                else:
                    line = f"🇪🇺 EUR/RUB **{price}** __{change}__"
                    list_currency.append(line)

                cache_data[f"{name}/RUB"] = line

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

        for name, url in urls.items():
            item = cache_data.get(url, None)
            if item is None:
                _, price, change = parse_body(url, name, headers)
                line = ""

                if name == "EUR/USD":
                    line = f"🇪🇺 {name} **{price}** __{change}__"
                    list_currency.append(line)
                elif name == "GBP/USD":
                    line = f"🇬🇧 {name} **{price}** __{change}__"
                    list_currency.append(line)
                elif name == "CHF/USD":
                    line = f"🇨🇭 {name} **{price}** __{change}__"
                    list_currency.append(line)
                elif name == "JPY/USD":
                    line = f"🇯🇵 {name} **{price}** __{change}__"
                    list_currency.append(line)
                elif name == "CNY/USD":
                    line = f"🇨🇳 {name} **{price}** __{change}__"
                    list_currency.append(line)

                cache_data[name] = line

            else:
                list_currency.append(item)

    elif crypto:
        pool = ThreadPool(processes=1)

        urls = {
            "Bitcoin USD": 'https://finance.yahoo.com/quote/BTC-USD?p=BTC-USD&.tsrc=fin-srch',
            "Ethereum USD": 'https://finance.yahoo.com/quote/ETH-USD?p=ETH-USD&.tsrc=fin-srch',
            "USDT": 'https://www.bestchange.net/ruble-cash-to-tether-trc20.html',
            "Dogecoin USD": 'https://finance.yahoo.com/quote/DOGE-USD?p=DOGE-USD&.tsrc=fin-srch',
            "Terra USD": 'https://finance.yahoo.com/quote/UST-USD?p=UST-USD&.tsrc=fin-srch',
            "GMT": 'https://finance.yahoo.com/quote/GMT3-USD?p=GMT3-USD&.tsrc=fin-srch',
            "Solana": 'https://finance.yahoo.com/quote/SOL-USD?p=SOL-USD&.tsrc=fin-srch',
            "GST": 'https://finance.yahoo.com/quote/GST2-USD?p=GST2-USD&.tsrc=fin-srch',
            "BNB": 'https://finance.yahoo.com/quote/BNB-USD?p=BNB-USD&.tsrc=fin-srch ',
            "GST_BSC": 'https://finance.yahoo.com/quote/GST3-USD?p=GST3-USD&.tsrc=fin-srch',
        }

        workers = []

        for name, url in urls.items():
            item = cache_data.get(name, None)
            if item is None:
                if name == "USDT":
                    workers.append(pool.apply_async(parse_body_USDT, (url, name, headers)))
                else:
                    workers.append(pool.apply_async(parse_body, (url, name, headers)))

            else:
                list_currency.append(item)

        for worker in workers:
            name, price, change = worker.get()
            if price == -100:
                price = "Нет данных о цене"
            if change == -100:
                change = "Нет данных об изменении"

            if name == "USDT":
                line = f"🔹 USDT: **{price}** __(лучший курс, по которому возможно купить)__"
            else:
                line = f"🔹 {name} **{price}** __{change}__"

            cache_data[name] = line
            list_currency.append(line)

    return '\n'.join(list_currency) + '\n\nАктуальные курсы: @bestchangenanbot'


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
    full_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(full_page.content, 'html.parser')
    price = -100
    change = -100
    try:
        price = soup.find("fin-streamer", {"data-field": "regularMarketPrice", "data-test": "qsp-price"}).text
        change = soup.find("fin-streamer", {"data-field": "regularMarketChangePercent",
                                            "class": "Fw(500) Pstart(8px) Fz(24px)"}).text
    except Exception as e:
        print(e)

    return name, price, change


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
