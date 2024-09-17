# CHALLENGE-SANOFI

## Descrição

O **CHALLENGE-SANOFI** é um projeto acadêmico desenvolvido como parte de um desafio universitário. Iniciado no começo do ano letivo e entregue no final do ano, o projeto visa resolver problemas reais enfrentados por uma empresa parceira. 

Durante o desenvolvimento, os alunos têm a oportunidade de aplicar conhecimentos teóricos e práticos em um ambiente colaborativo. Dependendo da qualidade e inovação do projeto, há a possibilidade de participação em uma competição promovida pela faculdade, onde os melhores projetos são selecionados e apresentados à empresa parceira. 

O objetivo principal é oferecer uma solução prática e eficaz que possa ser utilizada pela empresa, enquanto os participantes aprimoram suas habilidades em desenvolvimento de software e trabalho em equipe.

## Tecnologias

Este projeto utiliza as seguintes tecnologias:
- **Python**: A linguagem de programação principal usada para desenvolver o projeto.
- **Flask**: Um micro-framework para Python utilizado para construir a aplicação web.
- **pip**: O gerenciador de pacotes do Python, usado para instalar as dependências do projeto listadas no `requirements.txt`.
- **Virtualenv/venv**: Ferramentas para criar ambientes virtuais isolados para evitar conflitos entre pacotes de diferentes projetos.
- **SQLAlchemy** (opcional): ORM (Object Relational Mapper) para gerenciamento de banco de dados, caso esteja sendo usado.
- **Flask-Migrate** (opcional): Extensão para Flask para gerenciamento de migrações de banco de dados, se aplicável.
- **Jinja2**: Motor de templates integrado ao Flask, usado para renderizar arquivos HTML.
- **HTML/CSS/JavaScript**: Tecnologias para desenvolvimento do frontend e estilização da interface do usuário.
- **Git**: Sistema de controle de versão utilizado para rastrear alterações no código e colaborar no desenvolvimento.
- **`.env`**: Arquivo usado para armazenar variáveis de ambiente, como chaves secretas e URLs de banco de dados.
- **pytest** (opcional): Framework de testes utilizado para garantir a qualidade e a integridade do código.
- **Markdown**: Usado para criar o arquivo de documentação `README.md`.

## Instalação

Para configurar e executar o projeto localmente, siga estas etapas:

1. **Clone o repositório**:
    ```bash
    git clone https://github.com/feliperogai/Challenge-Sanofi.git
    cd challenge-sanofi

2. **Crie um ambiente virtual**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate`

3. **Instale as dependências**:
    ```bash
    pip install -r requirements.txt

4. **Configure as variáveis de ambiente**:
    ```bash
    SECRET_KEY=your_secret_key
    DATABASE_URL=your_database_url

5. **Execute as migrações**:
    ```bash
    flask db upgrade  # Ou o comando apropriado para suas migrações

6. **Inicie a aplicação**:
    ```bash
    python run.py




