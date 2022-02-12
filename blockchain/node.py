import requests
from uuid import uuid4
from quart import Quart, jsonify, request
from urllib.parse import urlparse
from node.blockchain import Blockchain
from node import utils

app = Quart(__name__)

class Node:
  def __init__(self, blockchain, identifier):
    self.blockchain = blockchain
    self.identifier = identifier
    self.neighbours = set()

# Get this node's identifier or create it
try:
  with open("./data/node.db", 'r') as f:
    node_identifier = f.read()
    f.close()
except:
  with open("./data/node.db", 'w') as f:
    node_identifier = str(uuid4()).replace('-', '')
    f.write(node_identifier)
    f.close()

blockchain = Blockchain()
blockchain.load()

node = Node(blockchain, node_identifier)

@app.route("/submit-proof", methods=["POST"])
async def check_hash():
  req = await request.get_json()
  if not req:
    return "Bad request", 400
  # Run the algorithm
  # (Miner's job)
  # last_block = blockchain.last_block
  # last_proof = last_block['proof']
  proof = req.get("proof")
  wallet = req.get("wallet")
  # proof = blockchain.proof_of_work(last_proof)

  if not (proof and wallet):
    return "Invalid request body", 400

  last_block = blockchain.last_block
  last_hash = utils.hash_block(last_block)
  if not utils.valid_proof(last_hash, last_block["proof"], proof):
    return "Invalid proof", 400

  # Mining reward
  # The sender is '0' to signify that this node has mined a new coin
  blockchain.new_transaction(
    sender='0',
    recipient=wallet,
    amount=1,
    signature='',
    reward=True
  )

  # Forge new block by adding it to the chain
  previous_hash = utils.hash_block(last_block)
  block = blockchain.new_block(proof, previous_hash)

  return jsonify({
    "message": "Block created",
    "index": block["index"],
    "transactions": block["transactions"],
    "proof": block["proof"],
    "timestamp": block["timestamp"],
    "previous_hash": block["previous_hash"]
  }), 200


@app.route("/balance", methods=["POST"])
async def check_balance():
  req = await request.get_json()
  if not req:
    return "Bad request", 400
  if "address" not in req:
    return "Missing address", 400

  balance = blockchain.get_balance(req["address"])
  return jsonify({ "message": balance })


@app.route("/transactions/new", methods=["POST"])
async def new_transaction():
  req = await request.get_json()
  required = ["sender", "recipient", "signature", "amount"]
  if not all(k in req for k in required):
    return "Missing values", 400

  response = blockchain.new_transaction(
    sender=req["sender"],
    recipient=req["recipient"],
    signature=req["signature"],
    amount=req["amount"]
  )

  if type(response) == int:
    return jsonify({ "message": f"Transaction will be added to Block {response}." }), 201

  return jsonify({ "message": response }), 409


@app.route("/chain", methods=["GET"])
async def get_chain():
  response = {
    "chain": blockchain.chain,
    "length": len(blockchain.chain)
  }

  return jsonify(response), 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=3000)
