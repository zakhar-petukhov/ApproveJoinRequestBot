from telethon import Button, TelegramClient, events
from telethon.tl.types import UpdateBotChatInviteRequester

import config
from redis import redis
from bot.utils import get_currency, get_or_create_user, cache_data, time_until_end_of_day

bot = TelegramClient('bot', config.API_ID, config.API_HASH).start(bot_token=config.BOT_TOKEN)


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
    count = await redis.get("count_request")
    if count is None:
        await redis.set("count_request", 1, time_until_end_of_day())
    else:
        await redis.incr("count_request")

    button_text = event.raw_text

    if button_text == "🇷🇺 RUB":
        item = cache_data.get(f"send_msg/rus", None)
        if item is None:
            await event.respond("Собираю данные")

        text = f"""
🇷🇺 Российский рубль

{await get_currency(ru=True)}
    """
        await event.respond(text)

    elif button_text == "🇺🇦 UAH":
        text = f"""
🇺🇦 Украинская гривна

{await get_currency(uah=True)}
    """
        await event.respond(text)

    elif button_text == "🌍 Прочие":
        await event.respond(await get_currency(other=True))

    elif button_text == "💲 Crypto":
        item = cache_data.get(f"send_msg/crypto", None)
        if item is None:
            await event.respond("Собираю данные")

        await event.respond(await get_currency(crypto=True))

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
