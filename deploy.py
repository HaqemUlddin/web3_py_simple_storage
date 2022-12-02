import json

import os

from dotenv import load_dotenv

import web3

from solcx import compile_standard

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

complied_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    }
)

with open("complied_code.json", "w") as file:
    json.dump(complied_sol, file)

# get bytecode
bytecode = complied_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abit
abi = complied_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]


# deploy to goerli testnet
w3 = web3.Web3(
    web3.Web3.HTTPProvider(
        "https://goerli.infura.io/v3/18fa694f1dcf420bb974d009e4bc3683"
    )
)

chain_id = 5
my_address = "0x9448c349748875535fbe504bdC362C42fC8B0626"
private_key = os.getenv("PRIVATE_KEY")

# create contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
# Build a signed transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# send this signed transaction

print("Deploying contract...")

tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Deployed!")

# working with contract

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# initial value of favorite numnber
print(simple_storage.functions.retrieve().call())

print("Updating contract..")

store_transaction = simple_storage.functions.store(2131).build_transaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_store_tx = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

transaction_hash = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)
transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)

print("Updated!")

print(simple_storage.functions.retrieve().call())
