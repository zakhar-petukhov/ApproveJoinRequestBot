from telethon import Button, TelegramClient, events
from telethon.tl.types import UpdateBotChatInviteRequester

import config
from bot.utils import get_currency, get_or_create_user

bot = TelegramClient('bot', config.API_ID, config.API_HASH)

welcome_text = "Привет! Этот бот показывает актуальный курс фиатных валют и криптовалют."


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    who = event.sender_id
    get_or_create_user(who)  # Ensure user is created or fetched

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

    await event.respond(welcome_text, buttons=keyboard)
    raise events.StopPropagation  # Stop further event propagation


@bot.on(events.NewMessage(pattern="(?i)🇷🇺 RUB|🌍 Прочие|🇺🇦 UAH|💲 Crypto"))
async def button_currency(event):
    button_text = event.raw_text

    text = ""
    if button_text == "🇷🇺 RUB":
        text = f"🇷🇺 Российский рубль\n\n{await get_currency(ru=True)}"
    elif button_text == "🇺🇦 UAH":
        text = f"🇺🇦 Украинская гривна\n\n{await get_currency(uah=True)}"
    elif button_text == "🌍 Прочие":
        text = await get_currency(other=True)
    elif button_text == "💲 Crypto":
        text = await get_currency(crypto=True)

    # Send collected data
    if text == "":
        return await event.respond("Не удалось собрать информацию")

    await event.respond(text)

    raise events.StopPropagation  # Stop further event propagation


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
        await get_or_create_user(user_id)  # Ensure the new user is created or fetched
        await bot.send_message(user_id, welcome_text, buttons=keyboard)
