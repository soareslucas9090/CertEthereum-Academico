// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CertificateRegistry {
    struct Cert {
        string nomeDoEstudante;
        string cpf;
        string nomeDaInstituicao;
        string curso;
        string descricaoDoCurso;
        string descricaoDoCertificado;
        uint256 dataDeEmissao;
        string cargaHoraria;
        string hashCertificado;
    }

    mapping(string => Cert[]) private certificados; 
    mapping(string => Cert) private certificadosPorHash;

    function emitirCertificado(
        string memory _cpf,
        string memory _nomeDoEstudante,
        string memory _nomeDaInstituicao,
        string memory _curso,
        string memory _descricaoDoCurso,
        string memory _descricaoDoCertificado,
        uint256 _dataDeEmissao,
        string memory _cargaHoraria,
        string memory _hashCertificado
    ) public {
        Cert memory novoCertificado = Cert(
            _nomeDoEstudante,
            _cpf,
            _nomeDaInstituicao,
            _curso,
            _descricaoDoCurso,
            _descricaoDoCertificado,
            _dataDeEmissao,
            _cargaHoraria,
            _hashCertificado
        );
        certificados[_cpf].push(novoCertificado);
        certificadosPorHash[_hashCertificado] = novoCertificado;
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
