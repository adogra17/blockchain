import json
import hashlib
import binascii
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random


def verify_transaction(transaction):
  """
    Validate a transaction signature

    :return: <bool> Whether the transaction signature is valid
  """

  # Ignore miner rewards
  if transaction["sender"] == '0':
    return True

  t = f"{transaction['sender']}{transaction['recipient']}{transaction['amount']}"
  public_key = RSA.import_key(binascii.unhexlify(transaction["sender"]))
  verifier = PKCS1_v1_5.new(public_key)
  hashed = SHA256.new(t.encode("utf-8"))
  return verifier.verify(hashed, binascii.unhexlify(transaction["signature"]))


def hash_block(block):
  block_string = json.dumps(block, sort_keys=True).encode()
  return hashlib.sha256(block_string).hexdigest()


def valid_proof(last_hash, last_proof, proof):
  guess = f"{last_hash}{last_proof}{proof}".encode()
  guess_hash = hashlib.sha256(guess).hexdigest()
  return guess_hash[:5] == "00000"


def valid_blockchain(blockchain):
  """
    Determine if a given blockchain is valid

    :param blockchain: <list> A blockchain

    :return: <bool> True if valid, False if not
  """

  last_block = blockchain.last_block
  current_index = 1

  while current_index < len(blockchain):
    block = blockchain[current_index]
    print(f'{last_block}')
    print(f'{block}')
    print("\n-----------\n")
    # Check that the hash of the block is correct
    if block["previous_hash"] != hash_block(last_block):
      print(f"Block {block['index']} has invalid hash for Block {last_block['index']}! Has Block {last_block['index']} been modified?")
      return False

    # Check that the Proof of Work is correct
    last_hash = hash_block(last_block)
    if not valid_proof(last_hash, last_block["proof"], block["proof"]):
      print(f"Invalid Proof of Work for Block {block['index']}.")
      return False

    last_block = block
    current_index += 1

  return True
