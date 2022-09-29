import os

import requests
from telethon import Button
import json

import jsonpickle

from admin.utils import send_async_send_message
from db.models import User


class Setting:
    def __init__(self, bot):
        self.bot = bot

    def get_json(self, name):
        data = None

        try:
            with open(name) as file:
                data = json.load(file)

        except FileNotFoundError:
            if name == 'mail.json':
                data = {'text': 'None', 'media': 'None', 'content': 'None', 'button': 'None', 'preview': 'False',
                        'entities': 'None'}

            with open(name, 'w') as file:
                file.write(json.dumps(data, indent=4, ensure_ascii=False))

        return data

    async def send_mail(self, preview=False, admin_id=None, **kwargs):
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
            await self.bot.send_message(admin_id, 'Ошибка! Добавьте текст или фото')
            return

        if text == 'None':
            text = None

        if web_preview == 'False':
            web_preview = False
        else:
            web_preview = True

        if button != 'None':
            name = button.split(' - ')[0:-1]
            name = ' '.join(name)
            url = button.split(' - ')[-1]

            keyboard = [[Button.url(name, url)]]

        else:
            keyboard = None

        if media == 'None':
            if preview is False:
                await send_async_send_message(self.bot, users, text, entities, web_preview, keyboard, None)

            else:
                await self.bot.send_message(admin_id, text, formatting_entities=entities, link_preview=web_preview,
                                            buttons=keyboard)

        else:
            path = media.split(':')[1]
            if preview is False:
                await send_async_send_message(self.bot, users, text, entities, web_preview, keyboard, None)

            else:
                await self.bot.send_file(admin_id, path, formatting_entities=entities, caption=text,
                                         buttons=keyboard)

    def change_value(self, name, key, value):
        data = self.get_json(name)
        data[key] = value

        with open(name, "w") as file:
            file.write(json.dumps(data, indent=4, ensure_ascii=False))

    def mail_text(self):
        data = self.get_json('mail.json')
        text = data['text'] if data['text'] != 'None' else '-'
        button = data['button'] if data['button'] != 'None' else '-'
        preview = '✅' if data['preview'] != 'False' else '❌'
        content = '✅' if data['content'] != 'False' else '❌'
        media = '✅' if data['media'] != "None" else '❌'

        text = f"""
__Сообщение для массовой рассылки:__

**Текст:**
{text}

**Кнопка:** 
{button}

Медиа** 
{media}

**Контент снизу:** 
{content}

Предпросмотр:** 
{preview}
"""
        return text

    def switch_preview(self):
        data = self.get_json('mail.json')

        if data['preview'] == 'False':
            self.change_value('mail.json', 'preview', 'True')

        elif data['preview'] == 'True':
            self.change_value('mail.json', 'preview', 'False')

    def clear_mail(self):
        self.change_value('mail.json', 'text', 'None')
        self.change_value('mail.json', 'media', 'None')
        self.change_value('mail.json', 'content', 'False')
        self.change_value('mail.json', 'button', 'None')
        self.change_value('mail.json', 'preview', 'False')
        self.change_value('mail.json', 'entities', 'None')

    async def download_file(self, file_id):
        file_name = await self.bot.download_media(file_id)
        file = open(file_name, 'rb')

        main_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(main_path, file_name)
        os.remove(path)

        return file

    async def upload_telegraph(self, file_id, content_type):
        file_name = await self.bot.download_media(file_id, "media")
        with open(file_name, 'rb') as file:
            data = requests.post('https://telegra.ph/upload', files={'file': ('file', file, content_type)}).json()
            url = "https://telegra.ph" + data[0]['src']
            return url

    def load_entities(self):
        data = self.get_json('mail.json')
        entities = data['entities']

        if entities != 'None':
            entities_data = json.loads(entities)
        else:
            entities_data = []

        return entities_data

    def save_entities(self, entities):
        entities = str(entities).replace("'", '\"')
        entities = str(entities).replace("None", 'null')

        self.change_value('mail.json', 'entities', str(entities))

    def add_offset(self):
        entities = self.load_entities()

        for e in entities:
            e['offset'] += 1

        self.save_entities(entities)

    def add_url(self, url):
        entities = self.load_entities()
        entities.append({'py/object': 'telethon.tl.types.MessageEntityTextUrl', 'offset': 0, 'length': 1, 'url': url})

        self.save_entities(entities)

    def change_url(self, url):
        entities = self.load_entities()
        entities[-1]['url'] = url
        self.save_entities(entities)

    def add_wordjoiner(self):
        data = self.get_json('mail.json')
        text = data['text']
        text = '⁠' + text

        self.change_value('mail.json', 'text', text)

    async def add_content(self, file_id, content_type):
        url = await self.upload_telegraph(file_id, content_type)
        data = self.get_json('mail.json')

        if data['content'] == 'False':
            self.add_offset()
            self.add_wordjoiner()
            self.change_value('mail.json', 'content', 'True')
            self.add_url(url)
        else:
            self.change_url(url)
