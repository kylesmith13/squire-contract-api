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

app.run()