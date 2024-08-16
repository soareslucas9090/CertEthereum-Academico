import os

from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
ALCHEMY_API_URL = os.environ.get("ALCHEMY_API_URL")
w3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))


if not w3.is_connected():
    raise Exception("Não foi possível conectar ao nó da Ethereum.")
