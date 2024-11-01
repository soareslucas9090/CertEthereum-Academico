import json
import os
from datetime import datetime

from dotenv import load_dotenv
from web3 import Web3
from web3.types import Wei

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
        "internal_id": certificate[0],
        "student_name": certificate[1],
        "cpf": certificate[2],
        "student_email": certificate[3],
        "institution_name": certificate[4],
        "activity": certificate[5],
        "activity_description": certificate[6],
        "certificate_description": certificate[7],
        "issue_date": datetime.fromtimestamp(certificate[8]).strftime("%Y-%m-%d"),
        "course_workload": certificate[9],
        "hash": certificate[10],
        "function": certificate[11],
        "type": certificate[12],
        "initial_date": datetime.fromtimestamp(certificate[13]).strftime("%Y-%m-%d"),
        "final_date": datetime.fromtimestamp(certificate[14]).strftime("%Y-%m-%d"),
        "local": certificate[15],
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
            id_interno = data["internal_id"]
            email_do_estudante = data["student_email"]
            funcao = data["function"]
            tipo = data["type"]
            data_inicial = data["initial_date"]
            data_final = data["final_date"]
            local = data["local"]
            atividade = data["activity"]
            descricao_da_atividade = data["activity_description"]
            descricao_do_certificado = data["certificate_description"]
            data_de_emissao = data["issue_date"]
            carga_horaria = data["course_workload"]
            hash_certificado = hashlib.sha256(str(data).encode()).hexdigest()

            duplicated_cert = contract.functions.buscarCertificadoPorHash(
                hash_certificado
            ).call()

            if duplicated_cert[0] == "":
                block = w3.eth.get_block("latest")  # Obter o bloco mais recente
                base_fee = (
                    block.get("baseFeePerGas", 0) * 1.2
                )  # Valor base da transação

                cert_data = (
                    id_interno,
                    nome_do_estudante,
                    cpf,
                    email_do_estudante,
                    nome_da_instituicao,
                    atividade,
                    descricao_da_atividade,
                    descricao_do_certificado,
                    data_de_emissao,
                    carga_horaria,
                    hash_certificado,
                    funcao,
                    tipo,
                    data_inicial,
                    data_final,
                    local,
                )

                try:
                    gas_limit = contract.functions.emitirCertificado(
                        cert_data
                    ).estimate_gas({"from": account_address})
                except Exception as e:
                    print(e)

                print("Gas Limit:", gas_limit)

                try:
                    transaction = contract.functions.emitirCertificado(
                        cert_data
                    ).build_transaction(
                        {
                            "from": account_address,
                            "nonce": w3.eth.get_transaction_count(
                                account_address, "pending"
                            ),
                            "gas": gas_limit,
                            "maxFeePerGas": Wei(int(base_fee) + w3.to_wei("2", "gwei")),
                            "maxPriorityFeePerGas": w3.to_wei(
                                "2", "gwei"
                            ),  # Configure aqui uma "gorjeta" para mineradores para que a transação seja processada mais rapidamente
                        }
                    )
                except Exception as e:
                    print(e)
                    return "error on buildding transaction"

                print("Transaction built successfully")

                signed_txn = w3.eth.account.sign_transaction(
                    transaction, private_key=private_key
                )

                try:
                    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                    print(f"Hash da transação enviada: {tx_hash.hex()}")

                except Exception as e:
                    print(e)

                print("TX hash:", tx_hash.hex())

                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

                print(f"Gas usado na transação: {tx_receipt['gasUsed']}")

                return {
                    "transaction_hash": tx_receipt["transactionHash"].hex(),
                    "certificate_hash": hash_certificado,
                }

            else:
                return ""

        elif op == 2:
            cpf = data["search_cpf"]
            certificates = contract.functions.buscarCertificadosPorCPF(cpf).call()
            if certificates:
                result = []

                for cert in certificates:
                    result.append(to_dict(cert))

                return result

            return []

        elif op == 3:
            hash_cert = data["search_hash"]
            cert = contract.functions.buscarCertificadoPorHash(hash_cert).call()

            if cert[0] != "":
                return to_dict(cert)

            return []

        else:
            raise
    else:
        raise
