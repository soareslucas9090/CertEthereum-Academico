// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CertificateRegistry {
    struct Cert {
        string idInterno;
        string nomeDoEstudante;
        string cpf;
        string emailEstudante;
        string nomeDaInstituicao;
        string atividade; 
        string descricaoDaAtividade; 
        string descricaoDoCertificado;
        uint256 dataDeEmissao;
        string cargaHoraria;
        string hashCertificado;
        string funcao; // valores permitidos: "executou", "organizou", "participou"
        string tipo; // valores permitidos: "projeto", "evento", "curso"
        uint256 dataInicial;
        uint256 dataFinal;
        string local;
    }

    mapping(string => Cert[]) private certificados; 
    mapping(string => Cert) private certificadosPorHash;

    function emitirCertificado(Cert memory novoCertificado) public {
        // Validação da função
        require(
            keccak256(abi.encodePacked(novoCertificado.funcao)) == keccak256("executou") ||
            keccak256(abi.encodePacked(novoCertificado.funcao)) == keccak256("organizou") ||
            keccak256(abi.encodePacked(novoCertificado.funcao)) == keccak256("participou"),
            "Funcao invalida"
        );

        // Validação do tipo
        require(
            keccak256(abi.encodePacked(novoCertificado.tipo)) == keccak256("projeto") ||
            keccak256(abi.encodePacked(novoCertificado.tipo)) == keccak256("evento") ||
            keccak256(abi.encodePacked(novoCertificado.tipo)) == keccak256("curso"),
            "Tipo invalido"
        );

        certificados[novoCertificado.cpf].push(novoCertificado);
        certificadosPorHash[novoCertificado.hashCertificado] = novoCertificado;
    }

    function buscarCertificadosPorCPF(string memory _cpf)
        public
        view
        returns (Cert[] memory)
    {
        return certificados[_cpf];
    }

    function buscarCertificadoPorHash(string memory _hashCertificado)
        public
        view
        returns (Cert memory)
    {
        return certificadosPorHash[_hashCertificado];
    }
}