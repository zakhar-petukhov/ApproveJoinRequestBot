import asyncio

from db.models import User


async def send_async_send_message(bot, users, text, entities, web_preview, keyboard, file):
    tasks = []
    count = 0

    for user in users:
        user_id = user["user_id"]
        tasks.append(send_or_update_active(bot, user_id, text, entities, web_preview, keyboard, file))

        count += 1
        if count > 10:
            count = 0
            await asyncio.gather(*tasks)
            await asyncio.sleep(2)
            tasks = []

    if len(tasks) > 0:
        await asyncio.gather(*tasks)


async def send_or_update_active(bot, user_id, text, entities, web_preview, keyboard, file):
    try:
        if file is not None:
            await bot.send_file(user_id, file, formatting_entities=entities, caption=text,
                                buttons=keyboard,
                                allow_cache=False)
        else:
            await bot.send_message(user_id, text, formatting_entities=entities, link_preview=web_preview,
                                   buttons=keyboard)

    except Exception:
        User.update(active=False).where(User.user_id == user_id).execute()
