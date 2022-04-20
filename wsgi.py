from app.main import app, blahBlah
import asyncio

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        print('this happening?')
        loop.run_until_complete(blahBlah())
