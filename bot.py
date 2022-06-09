from enum import Enum, auto

import jsonpickle
from telethon import Button, TelegramClient, events
from telethon.tl.types import UpdateBotChatInviteRequester

import config
from models import User
from utils import Setting, get_currency, get_or_create_user

admins = [594400511, 1260871881, 149031756, 583525749, 952644352]

bot = TelegramClient('bot', config.API_ID, config.API_HASH).start(bot_token=config.BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/admin'))
async def admin(event):
    who = event.sender_id
    if who in admins:
        keyboard = [
            [Button.inline("Посмотреть статистику", b"statistics")],
            [Button.inline("Создать рассылку", b"mailing")],
        ]
        await event.respond("С возвращением!", buttons=keyboard)


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    who = event.sender_id
    get_or_create_user(who)

    keyboard = [
        [
            Button.text("🇷🇺 RUB", resize=True),
            Button.text("🌍 Прочие", resize=True),
        ],
        [
            Button.text("🇺🇦 UAH", resize=True),
            Button.text("💲 Crypto", resize=True),
        ],
    ]
    text = """
Привет! Этот бот показывает актуальный курс фиатных валют и криптовалют.
        """
    await event.respond(text, buttons=keyboard)
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern="(?i)🇷🇺 RUB|🌍 Прочие|🇺🇦 UAH|💲 Crypto"))
async def button_currency(event):
    user_id = event.message.peer_id.user_id
    button_text = event.raw_text

    # try:
    #     await bot.get_permissions(config.SUBSCRIBE_CHANNEL, user_id)
    # except:
    #     await event.respond("Для использования бота необходима подписка на @idei_biznes.")
    #     return

    if button_text == "🇷🇺 RUB":
        text = f"""
🇷🇺 Российский рубль

{get_currency(ru=True)}
    """
        await event.respond(text)

    elif button_text == "🇺🇦 UAH":
        text = f"""
🇺🇦 Украинская гривна

{get_currency(uah=True)}
    """
        await event.respond(text)

    elif button_text == "🌍 Прочие":
        await event.respond(get_currency(other=True))

    elif button_text == "💲 Crypto":
        await event.respond(get_currency(crypto=True))

    raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern="statistics"))
async def statistics(event):
    total_users = User.select().count()
    active_users = User.select().where(User.active == True).count()
    text = f"""
Вот немного статистики о боте:

Количество пользователей: **{active_users}**
"""
    user_id = event.sender_id
    msg_id = event.message_id

    await bot.edit_message(user_id, message=msg_id, text=text)
    raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern="mailing"))
async def mailing(event):
    s = Setting()
    text = s.mail_text()

    keyboard = [
        [
            Button.text("✅ Разослать сообщение", resize=True),
            Button.text("👁 Предпросмотр сообщения", resize=True),
        ],
        [
            Button.text("✏️ Изменить текст", resize=True),
            Button.text("🌄 Изменить фото", resize=True),
        ],
        [
            Button.text("📼 Изменить видео", resize=True),
            Button.text("🖼 Изменить контент снизу", resize=True),
        ],
        [
            Button.text("🌍 Изменить кнопку", resize=True),
            Button.text("🖥 Вкл/выкл предпросмотр", resize=True),
        ],
        [
            Button.text("🗑 Очистить сообщение", resize=True),
            Button.text("❌ Отменить рассылку", resize=True),
        ]
    ]

    user_id = event.sender_id

    await bot.send_message(user_id, text, buttons=keyboard, parse_mode='html', link_preview=False)
    raise events.StopPropagation


@bot.on(events.ChatAction)
async def handler(event):
    if type(event.original_update) == UpdateBotChatInviteRequester:
        user_id = event.user_id
        keyboard = [
            [
                Button.text("🇷🇺 RUB", resize=True),
                Button.text("🌍 Прочие", resize=True),
            ],
            [
                Button.text("🇺🇦 UAH", resize=True),
                Button.text("💲 Crypto", resize=True),
            ],
        ]
        get_or_create_user(user_id)
        await bot.send_message(event.user_id,
                               "Привет! Этот бот показывает актуальный курс фиатных валют и криптовалют.",
                               buttons=keyboard)


class State(Enum):
    WAIT_TEXT = auto()
    WAIT_PHOTO = auto()
    WAIT_VIDEO = auto()
    WAIT_CONTENT = auto()
    WAIT_BUTTON = auto()


conversation_state = {}


@bot.on(events.NewMessage)
async def handler(event):
    who = event.sender_id
    state = conversation_state.get(who)

    if who not in admins:
        return

    text = event.raw_text
    s = Setting()

    if text.lower() == 'отмена':
        del conversation_state[who]
        await mailing(event)

    if state is None:
        if text != '':
            keyboard_cancel = [
                [
                    Button.text("Отмена", resize=True),
                ]
            ]

            if text == '/admin':
                return

            elif text == '✏️ Изменить текст':
                await event.respond('Отправьте ваш текст', buttons=keyboard_cancel)
                conversation_state[who] = State.WAIT_TEXT

            elif text == '🌄 Изменить фото':
                await event.respond('Отправьте ваше фото (как файл)', buttons=keyboard_cancel)
                conversation_state[who] = State.WAIT_PHOTO

            elif text == '📼 Изменить видео':
                await event.respond('Отправьте ваше видео', buttons=keyboard_cancel)
                conversation_state[who] = State.WAIT_VIDEO

            elif text == '🖼 Изменить контент снизу':
                await event.respond('Отправьте ваш контент (фото / GIF / видео):', buttons=keyboard_cancel)
                conversation_state[who] = State.WAIT_CONTENT

            elif text == '🌍 Изменить кнопку':
                await event.respond('Отправьте текст для кнопки и ссылку. Например Google|google.ru:',
                                    buttons=keyboard_cancel)
                conversation_state[who] = State.WAIT_BUTTON

            elif text == '🖥 Вкл/выкл предпросмотр':
                s.switch_preview()
                await mailing(event)

            elif text == '✅ Разослать сообщение':
                await event.respond('Рассылка была запущена')
                await s.send_mail(preview=False, admin_id=who)

            elif text == '👁 Предпросмотр сообщения':
                await s.send_mail(preview=True, admin_id=who)

            elif text == '🗑 Очистить сообщение':
                s.clear_mail()
                await mailing(event)

            elif text == '❌ Отменить рассылку':
                await start(event)

    elif state == State.WAIT_TEXT:
        text = event.message.message

        if event.message.entities:
            entities = jsonpickle.encode(event.message.entities)
        else:
            entities = 'None'

        if text.lower() != 'отмена':
            s.change_value('mail.json', 'text', text)
            s.change_value('mail.json', 'entities', entities)
            s.change_value('mail.json', 'content', 'False')

        del conversation_state[who]
        await mailing(event)

    elif state == State.WAIT_PHOTO:
        try:
            file_id = event.file.id
            file_name = event.file.name
        except:
            await event.respond('Отправьте ваше фото (как файл)')
            return

        mime_type = event.media.document.mime_type
        if '.gif' in file_name:
            content_type = 'animation'
        elif 'image' in mime_type:
            content_type = 'photo'
        else:
            await event.respond('Отправьте ваше фото (как файл)')
            return

        if content_type == 'photo':
            file = await bot.download_media(event.media)
        else:
            file = file_id

        s.change_value('mail.json', 'media', f'{content_type}:{file}')

        del conversation_state[who]
        await mailing(event)

    elif state == State.WAIT_VIDEO:
        try:
            file_id = event.file.id
        except:
            await event.respond('Отправьте ваше видео')
            return

        mime_type = event.media.document.mime_type
        if 'video' in mime_type:
            content_type = 'video'
        else:
            await event.respond('Отправьте ваше видео')
            return

        s.change_value('mail.json', 'media', f'{content_type}:{file_id}')

        del conversation_state[who]
        await mailing(event)

    elif state == State.WAIT_CONTENT:
        try:
            file_id = event.file.id
            file_name = event.file.name
        except:
            await event.respond('Отправьте ваш файл как фото или видео')
            return

        mime_type = event.media.document.mime_type
        if 'image' in mime_type:
            content_type = 'photo'
        elif '.gif' in file_name:
            content_type = 'animation'
        elif 'video' in mime_type:
            content_type = 'video'
        else:
            await event.respond('Отправьте ваш файл как фото или видео')
            return

        await s.add_content(file_id, content_type)
        s.change_value('mail.json', 'preview', 'True')

        del conversation_state[who]
        await mailing(event)

    elif state == State.WAIT_BUTTON:
        text = event.message.message

        if text.lower() != 'отмена':
            s.change_value('mail.json', 'button', text)

        del conversation_state[who]
        await mailing(event)
