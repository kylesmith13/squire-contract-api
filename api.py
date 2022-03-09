import flask
from flask import request, jsonify
import config
import json
import utils
from web3 import Web3

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/heroes/<int:id>', methods=['GET'])
def heroes(id):
  hero = get_hero(id)
  return jsonify(hero)

@app.route('/auctions/<int:id>', methods=['GET'])
def auctions(id):
  auction = get_auction(id)
  return jsonify(auction)

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


def get_auction(token_id):
  w3 = Web3(Web3.HTTPProvider(config.harmony_url))
  abi = json.loads(config.auction_abi)

  contract_address = Web3.toChecksumAddress(config.auction_contract_address)
  contract = w3.eth.contract(contract_address, abi=abi)
  auction = contract.functions.getAuction(token_id).call()
  return human_readable_auction(auction, token_id)

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

app.run()