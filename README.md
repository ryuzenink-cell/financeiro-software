# Financeiro Software

Sistema desktop de controle financeiro para MEIs, desenvolvido em **Python**, com interface gráfica em **PySide6** e banco de dados local em **SQLite**.

O objetivo do projeto é criar uma aplicação simples, organizada e escalável para ajudar pequenos empreendedores a controlar fornecedores, clientes, contas a pagar, contas a receber, fluxo de caixa e relatórios financeiros.

---

## Visão Geral

O **Financeiro Software** é um sistema administrativo inspirado em softwares empresariais de gestão, com foco inicial em MEIs e pequenos negócios.

Nesta primeira versão, o projeto já conta com:

- Interface gráfica desktop;
- Menu superior com módulos;
- Banco de dados SQLite local;
- Cadastro de fornecedores;
- Listagem de fornecedores em tabela;
- Busca por nome, documento, telefone ou e-mail;
- Cadastro, edição e exclusão de fornecedores;
- Organização do código em camadas.

---

## Tecnologias Utilizadas

- Python
- PySide6
- SQLite
- VS Code
- Git/GitHub

---

## Estrutura do Projeto

```txt
Financeiro-Software/
│
├── app/
│   ├── database/
│   │   ├── connection.py
│   │   └── schema.py
│   │
│   ├── repositories/
│   │   └── fornecedor_repository.py
│   │
│   ├── ui/
│   │   ├── main_window.py
│   │   └── fornecedores_page.py
│   │
│   └── config.py
│
├── data/
│   └── financeiro_teste.db
│
├── scripts/
│   └── popular_fornecedores.py
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Módulos Planejados

### Cadastros

- Fornecedores
- Clientes
- Produtos
- Serviços

### Financeiro

- Contas a pagar
- Contas a receber
- Fluxo de caixa
- Categorias financeiras
- Formas de pagamento

### Fiscal

- Registro de notas fiscais
- Anexos de XML/PDF
- Controle de notas emitidas e recebidas

### Relatórios

- Relatório financeiro mensal
- Relatório de contas a pagar
- Relatório de contas a receber
- Relatório de fluxo de caixa
- Exportação para CSV/Excel/PDF

### Sistema

- Configurações da empresa
- Backup do banco de dados
- Preferências do sistema

---

## Como Executar o Projeto

### 1. Clone o repositório

```bash
git clone https://github.com/SEU-USUARIO/financeiro-software.git
```

Entre na pasta do projeto:

```bash
cd financeiro-software
```

---

### 2. Crie o ambiente virtual

No Windows:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```bash
.venv\Scripts\activate
```

---

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

### 4. Execute o sistema

```bash
python main.py
```

---

## Banco de Dados

O sistema utiliza SQLite como banco de dados local.

O arquivo do banco é criado automaticamente dentro da pasta:

```txt
data/
```

Por segurança, arquivos `.db`, `.sqlite` e `.sqlite3` não devem ser enviados ao GitHub.

---

## Funcionalidades Já Implementadas

- Criação automática das tabelas principais;
- Interface desktop com menu superior;
- Tela de fornecedores;
- Listagem de fornecedores;
- Busca de fornecedores;
- Cadastro de fornecedor;
- Edição de fornecedor;
- Exclusão de fornecedor;
- Banco local SQLite.

---

## Próximas Etapas

- Melhorar a interface visual da tela de fornecedores;
- Adicionar paginação na tabela;
- Criar tela de clientes;
- Criar tela de produtos e serviços;
- Criar contas a pagar;
- Criar contas a receber;
- Criar fluxo de caixa;
- Criar dashboard financeiro;
- Implementar exportação de dados;
- Criar instalador para Windows.

---

## Objetivo do Projeto

Este projeto tem como objetivo servir como:

- Aplicação real para pequenos empreendedores;
- Projeto de portfólio;
- Estudo prático de Python desktop;
- Estudo de banco de dados SQLite;
- Base para um futuro sistema financeiro mais completo.

---

## Status

Projeto em desenvolvimento.

Versão atual: `0.1.0`

---

## Autor

Desenvolvido por **Ryuzen**.
