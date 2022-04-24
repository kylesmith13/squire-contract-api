import flask
from flask import jsonify, request
import config
import json
import utils
from web3 import Web3
from web3._utils.events import get_event_data
from hexbytes import HexBytes
from app.logger import log_error

app = flask.Flask(__name__)


@app.route('/heroes/<int:id>', methods=['GET'])
def heroes(id):
    hero = get_hero(id)
    return jsonify(hero)


@app.route('/getAuctions', methods=['POST'])
def auction_filter():
    fromBlock = request.json['fromBlock']
    w3 = Web3(Web3.HTTPProvider(config.harmony_url))
    abi = json.loads(config.auction_abi)
    created_abi = json.loads(config.auction_created_event_abi)
    canceled_abi = json.loads(config.auction_canceled_event_abi)
    purchased_abi = json.loads(config.auction_successful_event_abi)

    contract_address = Web3.toChecksumAddress(config.auction_contract_address)

    # keccak hashed function head for an event
    auction_created = "0x9a33d4a1b0a13cd8ff614a080df31b4b20c845e5cde181e3ae6f818f62b6ddde"
    auction_canceled = "0xdb9cc99dc874f9afbae71151f737e51547d3d412b52922793437d86607050c3c"
    auction_purchased = "0xe40da2ed231723b222a7ba7da994c3afc3f83a51da76262083e38841e2da0982"
    latest = w3.eth.get_block_number()
    logs = w3.eth.get_logs(
        {"abi": abi, "address": contract_address, "topics": [auction_created], "fromBlock": fromBlock, "toBlock": latest})

    logs = logs + w3.eth.get_logs({"abi": abi, "address": contract_address, "topics": [
        auction_canceled], "fromBlock": fromBlock, "toBlock": latest})

    logs = logs + w3.eth.get_logs({"abi": abi, "address": contract_address, "topics": [
        auction_purchased], "fromBlock": fromBlock, "toBlock": latest})

    all_events = []
    for log in logs:
        # Convert raw JSON-RPC log result to human readable event by using ABI data
        # More information how processLog works here
        # https://github.com/ethereum/web3.py/blob/fbaf1ad11b0c7fac09ba34baff2c256cffe0a148/web3/_utils/events.py#L200
        HexBytes(auction_created) == log['topics'][0]
        if log['topics'][0] == HexBytes(auction_created):
            handle_events(created_abi, w3, log, all_events)
            # all_events.append(get_event_data(w3.codec, created_abi, log))
        elif log['topics'][0] == HexBytes(auction_canceled):
            handle_events(canceled_abi, w3, log, all_events)
        elif log['topics'][0] == HexBytes(auction_purchased):
            handle_events(purchased_abi, w3, log, all_events)

    return jsonify({"latest": latest, "events": all_events})


@ app.route('/getFilterChanges/<address>', methods=['GET'])
def get_auction_changes(address):
    w3 = Web3(Web3.HTTPProvider(config.harmony_url))
    return w3.eth.get_filter_changes(address)


def get_hero(hero_id):
    w3 = Web3(Web3.HTTPProvider(config.harmony_url))
    abi = json.loads(config.contract_abi)

    contract_address = Web3.toChecksumAddress(config.contract_address)
    contract = w3.eth.contract(contract_address, abi=abi)
    contract_entry = contract.functions.getHero(hero_id).call()

    hero = {}
    tuple_index = 0

    hero['id'] = contract_entry[tuple_index]
    tuple_index = tuple_index + 1
    tuple_index = tuple_index + 1

    extra = utils.parse_extra(contract_entry[tuple_index][0])
    hero['rarity'] = contract_entry[tuple_index][2]
    hero['shiny'] = contract_entry[tuple_index][3]
    hero['gen'] = contract_entry[tuple_index][4]
    hero['main_class'] = contract_entry[tuple_index][8]
    hero['sub_class'] = contract_entry[tuple_index][9]
    hero.update(extra)

    tuple_index = tuple_index + 1

    # HeroState
    hero['level'] = contract_entry[tuple_index][3]
    tuple_index = tuple_index + 1

    return hero


def human_readable_auction(auction, hero_id):
    human_readable = {}
    human_readable['auction_id'] = auction[0]
    human_readable['starting_price'] = auction[2]
    human_readable['ending_price'] = auction[3]
    human_readable['duration'] = auction[4]
    human_readable['started_at'] = auction[5]
    human_readable['hero_id'] = hero_id
    human_readable['token_id'] = hero_id

    return human_readable


def handle_events(abi, w3, log, events):
    event_data = get_event_data(w3.codec, abi, log)
    event_details = {}
    event_details['type'] = event_data['event']
    for key, value in event_data['args'].items():
        if key in ["startingPrice", "endingPrice", "totalPrice"]:
            # convert our number so its easier to handle
            event_details[key] = w3.fromWei(value, 'ether')
        else:
            event_details[key] = value

    events.append(event_details)
