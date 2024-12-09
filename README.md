# CertEthereum
CertEthereum é uma aplicação que utiliza a tecnologia blockchain Ethereum para emissão, armazenamento e validação de certificados acadêmicos. Desenvolvido como parte de um Trabalho de Conclusão de Curso, o sistema combina segurança, descentralização e acessibilidade para transformar a gestão de credenciais acadêmicas.

## 🎯 Objetivo
Proporcionar uma solução confiável e eficiente para instituições de ensino, estudantes e empregadores, garantindo autenticidade, imutabilidade e facilidade de verificação dos certificados emitidos.

## 🚀 Funcionalidades
Consulta Pública de Certificados: Qualquer pessoa pode consultar certificados por CPF ou hash.

Emissão em Blockchain: Certificados são registrados diretamente na blockchain Ethereum.

Login Restrito para Instituições: Apenas instituições podem emitir certificados.

Envio de Certificados por E-mail: Envia o certificado para o e-mail do aluno com os principais dados e PDF anexo.

API RESTful Documentada: Para integração com outros sistemas.

Interface Frontend Intuitiva: Para busca e submissão de certificados.
## 🛠️ Tecnologias Utilizadas
Blockchain: Ethereum - 
<img align="center" alt="Python" height="40" src="https://cdn.worldvectorlogo.com/logos/ethereum-1.svg">

Contratos Inteligentes: Solidity - 
<img align="center" alt="Python" height="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/solidity/solidity-original.svg">

Backend: Django, Django REST Framework - 
<img align="center" alt="Python" height="40" src="https://cdn.worldvectorlogo.com/logos/django.svg"><span>&nbsp;&nbsp;&nbsp;</span><img align="center" alt="Python" height="50" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/djangorest/djangorest-original.svg">

Frontend: Bootstrap - 
<img align="center" alt="Python" width="40" src="https://cdn.worldvectorlogo.com/logos/bootstrap-4.svg">    

Integração com Blockchain: Alchemy SDK, Web3.py - 
<img align="center" alt="Python" height="40" src="https://www.datocms-assets.com/105223/1701819587-logo.svg">  

Banco de Dados: PostgreSQL - 
<img align="center" alt="Python" height="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/postgresql/postgresql-original.svg">  

## 🖥️ Arquitetura
### Backend
Recebe as requisições via API REST.

Processa e envia os dados para a blockchain Ethereum.

Retorna o status e armazena metadados em um banco de dados relacional para indexação (esta parte é opcional, já que os únicos dados obrigatórios a serem guardados são os de login das Instituições).
### Frontend
Interface para busca e emissão de certificados.

Comunicação com o backend via API.
## 📦 Instalação e Configuração
Clone o repositório:

```bash
git clone https://github.com/seu-usuario/CertEthereum.git
cd CertEthereum
```
Crie e ative um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
```

Instale as dependências:

```bash
pip install -r requirements.txt
```
Configure as variáveis de ambiente em um arquivo .env na raiz do projeto:

```env
ALCHEMY_API_URL=<sua_api_alchemy>
ETH_ACCOUNT=<endereço_ethereum>
ETH_PRIVATE_KEY=<chave_privada>
DEBUG=True
DATABASE_URL=<sua_url_banco>
EMAIL_HOST_USER=<seu_email>
EMAIL_HOST_PASSWORD=<senha_email>
```
Realize as migrações:

```bash
python manage.py migrate
```
Inicie o servidor:

```bash
python manage.py runserver
```
(Opcional) Inicie o frontend: Configure o servidor do frontend para comunicar-se com a API.

## 📝 Uso
Acesse o sistema no navegador.

Utilize as opções de login para instituições ou de busca para usuários públicos.

Emita certificados ou realize consultas conforme necessário.
## 🧪 Testando na Rede de Testes
A aplicação utiliza a rede de testes Sepolia. Para trocar para a rede principal Ethereum:

Altere a variável ALCHEMY_API_URL no .env.

Não são necessárias mudanças no código.
## 📖 Documentação da API
Acesse a documentação interativa Swagger em:

<url_do_servidor>/schema/swagger/

