import os

from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
ALCHEMY_API_URL = os.environ.get("ALCHEMY_API_URL")
w3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))

# Cria uma nova conta
new_account = w3.eth.account.create()
print(f"Endereço da conta: {new_account.address}")
print(f"Chave privada: {new_account._private_key.hex()}")
