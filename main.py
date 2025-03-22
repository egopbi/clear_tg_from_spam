import asyncio
import os
import time

from dotenv import load_dotenv
from telethon import TelegramClient

from delete_functions import clear_spam_dialogs
from utils.get_sesions import get_session_files
from utils.logger import logger
from utils.register_session import register_session


load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSIONS_DIRECTORY = os.getenv('SESSIONS_DIRECTORY')

NUM_WORKERS = os.getenv('NUM_WORKERS')
UNREAD_COUNT_TRIGGER = os.getenv('UNREAD_COUNT_TRIGGER')
MAX_MESSAGE_FOR_CHECKING = os.getenv('MAX_MESSAGE_FOR_CHECKING')
COUNT_OF_MY_MESSAGE_TRIGGER_FOR_GROUP = os.getenv('COUNT_OF_MY_MESSAGE_TRIGGER_FOR_GROUP')
COUNT_OF_MY_MESSAGE_TRIGGER_FOR_PERSONAL_CHAT = os.getenv(
    'COUNT_OF_MY_MESSAGE_TRIGGER_FOR_PERSONAL_CHAT'
    )
 

async def main():
    try:
        start = time.time()
        for session in get_session_files(SESSIONS_DIRECTORY):
            client = TelegramClient(session=session, api_id=API_ID, api_hash=API_HASH)
            await clear_spam_dialogs(client)
        
        end = time.time()
        logger.success(f'Measure time of execution "{main.__name__}" function: {end-start} s')
        
    except FileNotFoundError:
        logger.error(f"You need to create at least one session by register_session()")
        logger.info("Creating session")
        try:
            await register_session()
        except ValueError:
            logger.error(f'Please fill your API_ID and API_HASH')
    

if __name__ == '__main__':
    asyncio.run(main())