import os
import json
from client.miner import Miner
from client import utils
from client.process import check_balance, process_transaction

def mine():
  if utils.check_valid_wallet():
    miner = Miner()
    miner.mine()
  else:
    print("No wallet address given in configuration! Return to menu and create one.\n")


while True:
  print("Select a menu option:")
  if utils.check_valid_wallet():
    print("1) View wallet keypair")
  else:
    print("1) Create a new wallet")
  print("2) Create a new transaction")
  print("3) Mine")
  print("4) Check current balance")
  print("5) Exit")

  given = input()

  try:
    given = int(given)
    if given > 5 or given < 1:
      raise ValueError()

    elif given == 5:
      break
    elif given == 4:
      if utils.check_valid_wallet():
        check_balance()
        print("\n")
      else:
        print("No wallet address given in configuration! Return to menu and create one.\n")
    elif given == 3:
      print("Starting mining operation.\n")
      try:
        mine()
      except KeyboardInterrupt:
        continue
    elif given == 2:
      if utils.check_valid_wallet():
        recipient = input("Please enter recipient address: ")
        amount = input("Please enter transaction amount: ")

        try:
          formatted_amount = float(amount)
          process_transaction(recipient, formatted_amount)
          print("\n")
        except ValueError:
          print("Please provide a valid amount.\n")
      else:
        print("No wallet address given in configuration! Return to menu and create one.\n")
    elif given == 1:
      valid, wallet = utils.check_valid_wallet(give=True)
      # If wallet exists, print
      if valid:
        print("WALLET KEYPAIR:\n")
        print(f"Private:\n{wallet['private_key']}\n")
        print(f"Public:\n{wallet['public_key']}")
      # Create new wallet
      else:
        priv, pub = utils.create_wallet()

        with open("./client/config.json") as file:
          _in = json.load(file)
          if "wallet_keypair" not in _in:
            _in["wallet_keypair"] = {}
          _in["wallet_keypair"]["private_key"] = priv
          _in["wallet_keypair"]["public_key"] = pub

          with open("./client/config.json", "w") as out:
            out.write(json.dumps(_in, indent=4))

  except ValueError:
    print("Please select a valid option.\n")

