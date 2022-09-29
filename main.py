import logging

from admin.admin import admin_panel
from bot.bot import bot
from db.models import database, User, Price


def configure_database():
    database.connect()
    database.create_tables([User, Price])
    database.close()
    logging.info('Database has been configured')


def main():
    configure_database()
    admin_panel(bot)
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
