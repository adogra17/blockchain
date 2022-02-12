import json
import time
from functools import reduce
from collections import OrderedDict
from node import utils

class Blockchain:
  def __init__(self):
    self.chain = []
    self.current_transactions = []
    self.wallets = set()

  def load(self):
    # TODO Connect to Node network and obtain chain
    try:
      with open("./data/chain.json", mode='r') as f:
        data = json.loads(f.read())
        self.chain = []
        for block in data["chain"]:
          clean = {
            "index": block["index"],
            "proof": block["proof"],
            "timestamp": block["timestamp"],
            "previous_hash": block["previous_hash"],
            "transactions": [
              OrderedDict([
                ("sender", t["sender"]),
                ("recipient", t["recipient"]),
                ("signature", t["signature"]),
                ("amount", t["amount"])
              ]) for t in block["transactions"]
            ]
          }
          self.chain.append(clean)

        if "current_transactions" in data:
          self.current_transactions = [OrderedDict([
            ("sender", t["sender"]),
            ("recipient", t["recipient"]),
            ("signature", t["signature"]),
            ("amount", t["amount"])
          ]) for t in data["current_transactions"]]
    except (IOError, IndexError):
      # Create Genesis Block
      self.new_block(previous_hash=1, proof=100)


  def save(self):
    try:
      with open("./data/chain.json", mode='w') as f:
        f.write(json.dumps({
          "chain": self.chain,
          "current_transactions": self.current_transactions
        }))
    except IOError:
      print("Blockchain failed to save to disk!")


  def new_block(self, proof, previous_hash=None):

    block = {
      "index": len(self.chain) + 1,
      "proof": proof,
      "timestamp": time.time(),
      "previous_hash": previous_hash or utils.hash_block(self.last_block),
      "transactions": self.current_transactions
    }

    # Reset current transactions as they've been applied to the block
    self.current_transactions = []

    # Add new block
    self.chain.append(block)

    return block


  @property
  def last_block(self):
    return self.chain[-1]


  def get_balance(self, wallet):
    sends = [[t["amount"] for t in block["transactions"] if t["sender"] == wallet] for block in self.chain]
    unconfirmed_sends = [t["amount"] for t in self.current_transactions if t["sender"] == wallet]
    sends.append(unconfirmed_sends)
    sent = 0
    for t in sends:
      if len(t) > 0:
        sent += sum(t)

    receives = [[t["amount"] for t in block["transactions"] if t["recipient"] == wallet] for block in self.chain]
    received = 0
    for t in receives:
      if len(t) > 0:
        received += sum(t)

    # sent = reduce(lambda tx_sum, tx_amount: tx_sum + sum(tx_amount) if len(tx_amount) > 0 else tx_sum + 0, sends)
    # received = reduce(lambda tx_sum, tx_amount: tx_sum + sum(tx_amount) if len(tx_amount) > 0 else tx_sum + 0, receives)

    return received - sent


  def valid_transaction(self, transaction):
    balance = self.get_balance(transaction["sender"])
    return balance >= transaction["amount"], balance


  def new_transaction(self, sender, recipient, signature, amount, reward=False):
    transaction = OrderedDict([
      ("sender", sender),
      ("recipient", recipient),
      ("signature", signature),
      ("amount", amount)
    ])

    if reward == False:

      if not utils.verify_transaction(transaction):
        return f"Invalid transaction signature!"

      valid, balance = self.valid_transaction(transaction)
      if not valid:
        return f"Transaction amount {amount} exceeds balance {balance} of wallet {sender}."

    self.current_transactions.append(transaction)
    self.save()
    return self.last_block["index"] + 1
