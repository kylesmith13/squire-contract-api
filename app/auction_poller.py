import asyncio
import json
import config
import time
import requests

from app.logger import log_error
from websockets import connect
from hexbytes import HexBytes
from web3 import Web3
from web3._utils.events import get_event_data


def background_task():
    asyncio.run(poll_auction_data())


async def poll_auction_data():
    websock_address = "wss://ws.s0.t.hmny.io/"
    contract_address = Web3.toChecksumAddress(config.auction_contract_address)
    log_error("starting")
    try:
        async with connect(websock_address) as ws:
            print("connecting to websocket")
            await ws.send(json.dumps({"id": 1, "method": "eth_subscribe", "params": ["logs", {
                "address": contract_address,
                "topics": []}]
            }))
            subscription_response = await ws.recv()
            print(subscription_response)
            # you are now subscribed to the event
            # you keep trying to listen to new events (similar idea to longPolling)
            while True:
                w3 = Web3(Web3.HTTPProvider(config.harmony_url))
                created_abi = json.loads(config.auction_created_event_abi)
                canceled_abi = json.loads(config.auction_canceled_event_abi)
                purchased_abi = json.loads(config.auction_successful_event_abi)

                auction_created = "0x9a33d4a1b0a13cd8ff614a080df31b4b20c845e5cde181e3ae6f818f62b6ddde"
                auction_canceled = "0xdb9cc99dc874f9afbae71151f737e51547d3d412b52922793437d86607050c3c"
                auction_purchased = "0xe40da2ed231723b222a7ba7da994c3afc3f83a51da76262083e38841e2da0982"
                try:
                    # this timing out after 60 seconds might have been what was breaking the entire system. its quite possible
                    # that no messages came in for 60 seconds
                    message = await asyncio.wait_for(ws.recv(), timeout=240)
                    parsed_message = json.loads(message)
                    print(time.strftime("%b %d %Y %H:%M:%S"))
                    log = parsed_message['params']['result']
                    for idx, item in enumerate(log["topics"]):
                        log["topics"][idx] = bytes(HexBytes(item))

                    if log['topics'][0] == HexBytes(auction_created):
                        print("found created event")
                        event = handle_event(created_abi, w3, log)
                        send_event(event, "auctionCreated")
                        print(event)
                    if log['topics'][0] == HexBytes(auction_canceled):
                        print("found canceled event")
                        event = handle_event(canceled_abi, w3, log)
                        send_event(event, "auctionCanceled")
                        print(event)
                    if log['topics'][0] == HexBytes(auction_purchased):
                        print("found purchased event")
                        event = handle_event(purchased_abi, w3, log)
                        send_event(event, "auctionPurchased")
                        print(event)

                    pass
                except Exception as e:
                    log_error(e)
                    break
    except:
        await asyncio.sleep(2)
        await poll_auction_data()


def handle_event(abi, w3, log):
    event_data = get_event_data(w3.codec, abi, log)
    event_details = {}
    event_details['type'] = event_data['event']
    for key, value in event_data['args'].items():
        if key in ["startingPrice", "endingPrice", "totalPrice"]:
            # convert our number so its easier to handle
            event_details[key] = value / 1000000000000000000
        else:
            event_details[key] = value

    return event_details


def send_event(event, route):
    try:
        res = requests.post(config.elixir_url + route, json=event)
        dictFromServer = res.json()
        print('response from server:', dictFromServer)
    except Exception as e:
        print(e)
