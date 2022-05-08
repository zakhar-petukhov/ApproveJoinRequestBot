import logging

from bot import bot
from models import database, User

logging.basicConfig(
    format='%(asctime)s – %(levelname)s – %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)


def configure_database():
    database.connect()
    database.create_tables([User])
    database.close()
    logging.info('Database has been configured')


def main():
    configure_database()
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
