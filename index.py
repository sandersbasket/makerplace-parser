import threading, time
from modules import functions, db
from settings import settings

database: db.Database = db.Database('./database.db')

last_index_page: int = database.get_last_index_page()
start_index: int = 0 if last_index_page is None else last_index_page

while True:
    threading.Thread(target = functions.get_collections, args = (10, start_index)).start()
    start_index += 10
    time.sleep(settings.config['start_thread_sleep'])
