import json
import os
from datetime import datetime

from dotenv import load_dotenv
from web3 import Web3

"""
    Com a função abaixo é possível executar 3 ações diferentes:
    op == 1: Insere um certificado na rede pelo contrato gerado
    op == 2: Busca todos os certificados de um determinado CPF
    op == 3: Busca um certificado de acordo com o hash dele
    
    O valor de data deve condizer com a função consumida, onde para op == 1
        data deve ser uma lista com 8 elementos, sendo estes, em ordem:
        cpf, nome_do_estudante, nome_da_instituicao, curso, descricao_do_curso,
        escricao_do_certificado, data_de_emissao, carga_horaria

        Para op == 2, data deve ser uma lista de 1 elemento, sendo
            data[0] == cpf do aluno
            
        Para op == 3, data deve ser uma lista de 1 elemento, sendo
            data[0] == hash do certificado
    
    Caso op seja qualquer outro valor, é retornado uma exceção
    Caso as variáveis de ambiente não sejam corretamente carregadas é
        retornada uma exceção
"""


def to_dict(certificate):
    return {
        "student_name": certificate[0],
        "cpf": certificate[1],
        "institution_name": certificate[2],
        "course": certificate[3],
        "course_description": certificate[4],
        "certificate_description": certificate[5],
        "issue_date": datetime.fromtimestamp(certificate[6]).strftime("%Y-%m-%d"),
        "course_workload": certificate[7],
        "hash": certificate[8],
    }


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

            cpf = data["cpf"]
            nome_do_estudante = data["student_name"]
            nome_da_instituicao = data["institution_name"]
            curso = data["course"]
            descricao_do_curso = data["course_description"]
            descricao_do_certificado = data["certificate_description"]
            data_de_emissao = data["issue_date"]
            carga_horaria = data["course_workload"]
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

            signed_txn = w3.eth.account.sign_transaction(
                transaction, private_key=private_key
            )
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_receipt["transactionHash"].hex()

        elif op == 2:
            cpf = data["search_cpf"]
            certificates = contract.functions.buscarCertificadosPorCPF(cpf).call()
            if certificates:
                result = []

                for cert in certificates:
                    result.append(to_dict(cert))

                return result

            return "Sem Resultados"

        elif op == 3:
            hash_cert = data["search_hash"]
            cert = contract.functions.buscarCertificadoPorHash(hash_cert).call()

            if cert[0] != "":
                return to_dict(cert)

            return "Sem Resultados"

        else:
            raise
    else:
        raise
