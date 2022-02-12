import requests
import json
import time
import hashlib
from client import utils
config = json.load(open("./client/config.json"))


class Miner:
  def __init__(self):
    self.wallet = config.get("wallet_keypair")

  @staticmethod
  def valid_proof(last_hash, last_proof, proof):
    guess = f"{last_hash}{last_proof}{proof}".encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:5] == "00000"

  def mine(self):
    """
      Main mining loop
      
      Connects to node and obtains last block to hash and submit proofs of work
    """
    response = requests.get(f"http://{config.get('node_address', 'localhost:3000')}/chain")
    data = response.json()

    chain = data.get("chain", None)
    if not chain or len(chain) == 0:
      raise Exception("No chain retrieved")

    last_block = chain[-1]
    block_string = json.dumps(last_block, sort_keys=True).encode()
    last_hash = hashlib.sha256(block_string).hexdigest()
    proof = self.proof_of_work(last_hash, last_block["proof"])

    _, wallet = utils.check_valid_wallet(give=True)

    res = requests.post(f"http://{config.get('node_address', 'localhost:3000')}/submit-proof",
      json={
        "proof": proof,
        "wallet": wallet["public_key"]
      }
    )

    if res.status_code != 400:
      print("Proof accepted.")

    self.mine()

  def proof_of_work(self, last_hash, last_proof):
    proof = 0
    previous_time = time.time() * 1000

    # Mining loop
    while self.valid_proof(last_hash, last_proof, proof) is False:
      # Logger
      t = time.time() * 1000
      # print(t > previous_time + 1000.0)
      if t > (previous_time + 1000.0):
        # print(f"Mining proof {proof}") # TODO Change
        previous_time = t

      proof += 1

    print("Valid proof found.")
    return proof
