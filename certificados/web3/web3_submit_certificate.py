import json
import os

from dotenv import load_dotenv
from web3 import Web3

"""
    Com a função abaixo é possível executar 3 ações diferentes:
    op == 1: Insere um certificado na rede pelo contrato gerado
    op == 2: Busca todos os certificados de um determinado CPF
    op == 3: Busca um certificado de acordo com o hash dele
    
    Caso op seja qualquer outro valor, é retornado uma exceção
    Caso as variáveis de ambiente não sejam corretamente carregadas é
        retornada uma exceção
"""

def certs_interactions(op, data):
    load_dotenv()

    ALCHEMY_API_URL = os.environ.get("ALCHEMY_API_URL")

    if ALCHEMY_API_URL:
        w3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))
        account_address = os.environ.get("ACCOUNT_ETHEREUM", "")
        account_address = w3.to_checksum_address(account_address)

        private_key = os.environ.get("PRIVATE_KEY_ETHEREUM")

        contract_address_file = open("./certificados/web3/contract_address.txt", "r")
        contract_address = contract_address_file.read()
        contract_address = w3.to_checksum_address(contract_address)
        contract_address_file.close()

        abi_file = open("./certificados/web3/abi.json", "r")
        abi = abi_file.read()
        abi_file.close()

        contract = w3.eth.contract(address=contract_address, abi=abi)

        if op == 1:
            import hashlib
            
            cpf = data[0]
            nome_do_estudante = data[1]
            nome_da_instituicao = data[2]
            curso = data[3]
            descricao_do_curso = data[4]
            descricao_do_certificado = data[5]
            data_de_emissao = data[6]
            carga_horaria = data[7]
            hash_certificado = hashlib.sha256(str(data).encode()).hexdigest()

            
            transaction = contract.functions.emitirCertificado(
                cpf,
                nome_do_estudante,
                nome_da_instituicao,
                curso,
                descricao_do_curso,
                descricao_do_certificado,
                data_de_emissao,
                carga_horaria,
                hash_certificado,
            ).build_transaction(
                {
                    "from": account_address,
                    "nonce": w3.eth.get_transaction_count(account_address),
                    "gasPrice": w3.to_wei("25", "gwei"),
                }
            )
            # Calculando o gas estimado e adicionando na transação
            estimated_gas = w3.eth.estimate_gas(transaction)
            transaction["gas"] = estimated_gas
            
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            return (f"Transação bem-sucedida com hash: {tx_receipt["transactionHash"].hex()}")

        elif op == 2:
            cpf = data[0]
            certificates = contract.functions.buscarCertificadosPorCPF(cpf).call()

            return certificates
        
        elif op == 3:
            hash_cert = data[0]
            cert = contract.functions.buscarCertificadoPorHash(hash_cert).call()
            
            return cert

        else:
            raise
    else:
        raise
