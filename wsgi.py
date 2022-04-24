from app.main import app
from app.auction_poller import background_task
from app.logger import initialize_logger
import asyncio
import threading

if __name__ == "__main__":
    initialize_logger()
    th = threading.Thread(target=background_task)
    th.start()
    app.run()
