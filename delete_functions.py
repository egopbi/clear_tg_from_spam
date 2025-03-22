import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel

from utils.logger import logger


load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSIONS_DIRECTORY = os.getenv('SESSIONS_DIRECTORY')

NUM_WORKERS = int(os.getenv('NUM_WORKERS'))
UNREAD_COUNT_TRIGGER = int(os.getenv('UNREAD_COUNT_TRIGGER'))
COUNT_OF_MY_MESSAGE_TRIGGER_FOR_GROUP = int(os.getenv('COUNT_OF_MY_MESSAGE_TRIGGER_FOR_GROUP'))
COUNT_OF_MY_MESSAGE_TRIGGER_FOR_PERSONAL_CHAT = int(
    os.getenv('COUNT_OF_MY_MESSAGE_TRIGGER_FOR_PERSONAL_CHAT')
)


async def ensure_connected(client):
    """Переподключение при разрыве соединения"""
    if not client.is_connected():
        logger.warning("Reconnecting to Telegram...")
        await client.connect()
    if not await client.is_user_authorized():
        logger.error("Not authorized. Need to reauthorized")
        return False
    return True


async def del_if_spam(worker_id, dialog, client, my_id):
    unread_count = dialog.unread_count
    entity = dialog.entity

    if not await ensure_connected(client):
        logger.error(f"{worker_id}\t| Can't connect to work with the dialog: {dialog.name}")
        return None

    if unread_count >= UNREAD_COUNT_TRIGGER:
        # delete chat
        await client.delete_dialog(dialog)
        logger.success(f"{worker_id}\t| Delete dialog 'UNREAD_COUNT {unread_count}"
                       f" >= UNREAD_COUNT TRIGGER' with name '{dialog.name}")
        await asyncio.sleep(1)
        return None
    
    # BOT
    if isinstance(entity, User) and entity.bot:
        logger.info(f"{worker_id}\t| Bot: {dialog.name}")

    # CHAT WITH PERSON
    elif isinstance(entity, User) and not entity.bot:
        await chat_iteration(
            client, 
            dialog, 
            my_id, 
            worker_id, 
            COUNT_OF_MY_MESSAGE_TRIGGER_FOR_PERSONAL_CHAT
        )
        return None


    # GROUP CHAT OR SUPERGROUP
    elif isinstance(entity, Chat) or (isinstance(entity, Channel) and not entity.broadcast):
        await chat_iteration(
            client, 
            dialog, 
            my_id, 
            worker_id, 
            COUNT_OF_MY_MESSAGE_TRIGGER_FOR_GROUP
        )            
        return None

    # CHANNEL
    elif isinstance(entity, Channel) and entity.broadcast:
        logger.info(f"{worker_id}\t| Channel: {dialog.name}")

    # UNKNOWN TYPE
    else:
        logger.info(f"{worker_id}\t| Uknown type: {dialog.name}")

    await asyncio.sleep(1)


async def chat_iteration(client, dialog, my_id, worker_id, trigger):
    count_of_my_message = 0
    if trigger is COUNT_OF_MY_MESSAGE_TRIGGER_FOR_PERSONAL_CHAT:
        logger.info(f"{worker_id}\t| {str(dialog.name).upper()} is chat with person")
    elif trigger is COUNT_OF_MY_MESSAGE_TRIGGER_FOR_GROUP:
        logger.info(f"{worker_id}\t| {str(dialog.name).upper()} is group")
    else:
        logger.error(f"{worker_id}\t| error with trigger processing in {dialog.name}")


    try:
        async for _ in client.iter_messages(dialog, my_id):
            if count_of_my_message < trigger:
                count_of_my_message += 1
                await asyncio.sleep(1)
            else:
                logger.info(f"{worker_id}\t| {str(dialog.name).upper()} was saved. "
                            f"Count of my message is {count_of_my_message}")
                break

    except Exception as e:
        logger.error(f"{worker_id}\t| When work with {dialog.name} get an error '{e}'\n "
                     f"Type of Error: {type(e)}")
        
    if count_of_my_message < trigger:
        logger.success(f"{worker_id}\t| Delete {dialog.name}. Count of my message was "
                       f"{count_of_my_message}")
        
        await client.delete_dialog(dialog)



async def worker_fun(worker_id, queue, client, my_id):
    while True:
        dialog = await queue.get()
        try:
            await del_if_spam(worker_id, dialog, client, my_id)
        except Exception as e:
            logger.error(f"Ошибка у воркера {worker_id} при обработке {dialog.name}: {e}")
        finally:
            queue.task_done()


async def clear_spam_dialogs(client: TelegramClient):
    queue_list = [asyncio.Queue() for _ in range(NUM_WORKERS)]
    async with client:
        me = await client.get_me()

    my_id = me.id
    workers = [
        asyncio.create_task(worker_fun(worker_id, queue_list[worker_id], client, my_id))
        for worker_id in range(NUM_WORKERS)
    ]

    async with client:
        worker_id = 0
        async for dialog in client.iter_dialogs():
            # Динамически распределяем по воркерам (по кругу)
            await queue_list[worker_id].put(dialog)
            worker_id = (worker_id + 1) % NUM_WORKERS

    await asyncio.gather(*(queue.join() for queue in queue_list))

    for worker in workers:
        worker.cancel()
  