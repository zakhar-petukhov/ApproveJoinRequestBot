import asyncio

from telethon import Button
from telethon import events

from admin.settings import Setting
from bot.bot import start
from config import ADMINS_ID
from db.models import User


def admin_panel(bot):
    @bot.on(events.NewMessage(pattern='/admin'))
    async def admin(event):
        user_id = event.sender_id
        if user_id in ADMINS_ID:
            settings = Setting(bot=bot)
            settings.clear_mail()
            await admin_button(bot, user_id)

    @bot.on(events.CallbackQuery(pattern="statistics"))
    async def statistics(event):
        active_users = User.select().where(User.active == True).count()
        text = f"""
Вот немного статистики о боте:

Количество пользователей: **{active_users}**
    """
        user_id = event.sender_id
        msg_id = event.message_id

        await bot.edit_message(user_id, message=msg_id, text=text)

    @bot.on(events.CallbackQuery(data="mailing"))
    async def mailing(event):
        user_id = event.sender_id
        await event.delete()

        settings = Setting(bot=bot)
        text = settings.mail_text()

        keyboard = [
            [
                Button.text("✅ Разослать сообщение", resize=True),
                Button.text("👁 Предпросмотр сообщения", resize=True),
            ],
            [
                Button.text("✏️ Изменить текст", resize=True),
                Button.text("🌄 Изменить медиа", resize=True),
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

        await bot.send_message(user_id, text, buttons=keyboard, link_preview=False)

    @bot.on(events.NewMessage)
    async def handler(event):
        settings = Setting(bot=bot)

        user_id = event.sender_id
        if user_id not in ADMINS_ID:
            return

        text = event.raw_text
        if text.lower() == 'отмена':
            await mailing(event)

        keyboard_cancel = [[Button.text("Отмена", resize=True)]]

        if text == '/admin':
            return

        elif text == '✏️ Изменить текст':
            try:
                async with bot.conversation(user_id, timeout=180) as conv:
                    await conv.send_message('Отправьте ваш текст', buttons=keyboard_cancel)
                    response = await conv.get_response()
                    text = response.text

                    if text.lower() != 'отмена':
                        settings.change_value('mail.json', 'text', text)
                        settings.change_value('mail.json', 'entities', 'None')
                        settings.change_value('mail.json', 'content', 'False')

            except asyncio.TimeoutError:
                await bot.send_message(user_id, "Время ожидания вышло")

            await mailing(event)

        elif text == '🌄 Изменить медиа':
            async with bot.conversation(user_id) as conv:
                await conv.send_message('Отправьте ваше медиа', buttons=keyboard_cancel)
                response = await conv.get_response()
                file_id = response.file.id
                content_type = response.file.mime_type
                if 'video' not in content_type:
                    file = await bot.download_media(response.media, "media")
                    settings.change_value('mail.json', 'media', f'photo:{file}')

                else:
                    settings.change_value('mail.json', 'media', f'{content_type}:{file_id}')

                await mailing(event)

        elif text == '🖼 Изменить контент снизу':
            async with bot.conversation(user_id) as conv:
                await conv.send_message('Отправьте ваш контент (фото / GIF / видео)', buttons=keyboard_cancel)
                response = await conv.get_response()

                try:
                    file_id = response.file.id
                except:
                    await event.respond('Отправьте контект файлом')
                    return

                content_type = response.file.mime_type

                await settings.add_content(file_id, content_type)
                settings.change_value('mail.json', 'preview', 'True')

                await mailing(event)

        elif text == '🌍 Изменить кнопку':
            async with bot.conversation(user_id) as conv:
                await conv.send_message('''Отправьте текст для кнопки и ссылку. 
Например `Google - google.ru`''', buttons=keyboard_cancel)
                response = await conv.get_response()
                text = response.text

                if text.lower() != 'отмена':
                    settings.change_value('mail.json', 'button', text)

                await mailing(event)

        elif text == '🖥 Вкл/выкл предпросмотр':
            settings.switch_preview()
            await mailing(event)

        elif text == '✅ Разослать сообщение':
            await bot.send_message(user_id, "Рассылка началась")
            await settings.send_mail(preview=False, admin_id=user_id)

        elif text == '👁 Предпросмотр сообщения':
            await settings.send_mail(preview=True, admin_id=user_id)

        elif text == '🗑 Очистить сообщение':
            settings.clear_mail()
            await mailing(event)

        elif text == '❌ Отменить рассылку':
            settings.clear_mail()
            await start(event)


async def admin_button(bot, user_id):
    buttons = [
        [Button.inline("Посмотреть статистику", b"statistics")],
        [Button.inline("Создать рассылку", b"mailing")],
    ]

    await bot.send_message(user_id, "Здарова, фермер!", buttons=buttons)
