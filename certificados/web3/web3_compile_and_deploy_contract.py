import json
import os

import solcx as sol
from dotenv import load_dotenv
from web3 import Web3

"""
    Este código serve para compilar o contrato .sol em dois arquivos:
    abi.json: Contem o código ABI do contrato
    contract_address: Contem o endereço do contrato na Ethereum
"""


def compile_and_deploy_contract():
    load_dotenv()

    ALCHEMY_API_URL = os.environ.get("ALCHEMY_API_URL")
    if ALCHEMY_API_URL:
        w3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))

        account_address = os.environ.get("ACCOUNT_ETHEREUM", "")
        account_address = w3.to_checksum_address(account_address)

        private_key = os.environ.get("PRIVATE_KEY_ETHEREUM")
        sourceSolidity = open(r".\certificados\Solidity\certificado.sol", "r")
        contract_source_code = sourceSolidity.read()
        sourceSolidity.close()

        sol.install_solc("0.8.0")
        sol.set_solc_version("0.8.0")
        # Compilação do contrato Solidity
        compiled_sol = sol.compile_source(contract_source_code)
        contract_interface = compiled_sol["<stdin>:CertificateRegistry"]

        # Geração de ABI do contrato
        with open("./certificados/web3/abi.json", "w") as file:
            json.dump(contract_interface["abi"], file)

        # Preparação do contrato para implantação
        contract_certificate = w3.eth.contract(
            abi=contract_interface["abi"], bytecode=contract_interface["bin"]
        )

        # Uso de gas estimado
        estimated_gas = contract_certificate.constructor().estimate_gas(
            {"from": account_address}
        )

        # Construção da transação para implantar o contrato
        transaction = contract_certificate.constructor().build_transaction(
            {
                "from": account_address,
                "nonce": w3.eth.get_transaction_count(account_address),
                "gas": estimated_gas,
                "gasPrice": w3.to_wei("25", "gwei"),
            }
        )

        # Assinatura da transação com a chave privada
        signed_txn = w3.eth.account.sign_transaction(
            transaction, private_key=private_key
        )

        # Envio da transação para a rede
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Espera até que a transação seja confirmada
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        with open("./certificados/web3/contract_address.txt", "w") as file:
            file.write(str(tx_receipt["contractAddress"]))

        return tx_receipt["contractAddress"]

    else:
        return "Não foi possível carregar as variáveis de ambiente"
