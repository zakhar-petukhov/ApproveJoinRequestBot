import logging

from db.connection import database
from db.models import User, Price

logger = logging.getLogger(__name__)


def configure_database():
    try:
        if database.is_closed():
            database.connect()
        database.create_tables([User, Price], safe=True)
        logger.info('Database has been configured')
    except Exception as e:
        logger.error(f'Error during database setup: {e}')
        raise
    finally:
        if not database.is_closed():
            database.close()
