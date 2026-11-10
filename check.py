import asyncio
import csv
import os
from datetime import datetime, timezone
from telethon import TelegramClient, events
from telethon.tl.types import UserStatusOnline, UserStatusOffline

# --- НАСТРОЙКИ ---
# Данные можно получить на https://my.telegram.org/
API_ID = 12345678 # Замените на реальный API ID
API_HASH = 'abcd1234...' # Замените на реальный API HASH

# ID пользователя, за которым нужно следить
TARGET_USER_ID = 123456789 # Замените на реальный ID пользователя

# Название файла, куда будут сохраняться данные
LOG_FILE = 'user_activity_log.csv'

online_users = {}

client = TelegramClient('my_tracker_session', API_ID, API_HASH)

def log_to_csv(user_id, username, status, start_time, end_time, duration):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['UserID', 'Username', 'Status', 'OnlineAt', 'OfflineAt', 'DurationSeconds'])
        
        writer.writerow([
            user_id, 
            username, 
            status, 
            start_time.strftime('%Y-%m-%d %H:%M:%S'), 
            end_time.strftime('%Y-%m-%d %H:%M:%S'), 
            int(duration)
        ])
    print(f"Запись добавлена в {LOG_FILE}")

@client.on(events.UserUpdate)
async def user_update_handler(event):
    if event.user_id == TARGET_USER_ID:
        user = await client.get_entity(TARGET_USER_ID)
        username = user.username or user.first_name

        if isinstance(event.status, UserStatusOnline):
            if TARGET_USER_ID not in online_users:
                online_since = datetime.now(timezone.utc)
                online_users[TARGET_USER_ID] = online_since
                print(f"{username} (ID: {TARGET_USER_ID}) появился в сети в {online_since.strftime('%H:%M:%S')}")

        elif isinstance(event.status, UserStatusOffline):
            if TARGET_USER_ID in online_users:
                start_time = online_users.pop(TARGET_USER_ID)
                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()
                
                print(f"{username} (ID: {TARGET_USER_ID}) был в сети {int(duration)} секунд.")
                log_to_csv(TARGET_USER_ID, username, 'Offline', start_time, end_time, duration)

async def main():
    await client.start()
    print(f"Приложение запущено. Отслеживаю пользователя с ID: {TARGET_USER_ID}")
    print(f"Данные будут сохраняться в файл: {LOG_FILE}")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())