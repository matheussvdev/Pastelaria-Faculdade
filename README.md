# 🥟 Sistema de Gestão de Comandas — Pastelaria

## 📌 Sobre o projeto

O **Sistema de Gestão de Comandas** é um aplicativo desenvolvido como projeto acadêmico do curso de **Análise e Desenvolvimento de Sistemas**, com o objetivo de modernizar e simplificar o gerenciamento de pedidos e comandas de uma pastelaria.

A solução surgiu a partir da identificação de dificuldades reais no estabelecimento, especialmente no registro de pedidos, no acompanhamento das comandas e no fechamento das contas durante períodos de maior movimento.

O aplicativo busca proporcionar mais agilidade, organização e confiabilidade ao atendimento, reduzindo processos manuais e facilitando a gestão do negócio.

## 🎯 Objetivo

Desenvolver um Produto Mínimo Viável (MVP) capaz de auxiliar atendentes e administradores nas principais atividades operacionais de uma pastelaria.

**Objetivos específicos:**

- Digitalizar o registro e o gerenciamento de comandas.
- Automatizar o cálculo dos valores dos pedidos.
- Facilitar o acompanhamento de comandas abertas e fechadas.
- Reduzir erros operacionais e retrabalho.
- Disponibilizar informações gerenciais para o administrador.
- Oferecer uma interface simples, intuitiva e adequada à rotina do estabelecimento.

## 🔎 Problema identificado

Durante o diagnóstico realizado com o estabelecimento parceiro, foram identificadas dificuldades relacionadas ao controle manual de comandas e ao fechamento das contas.

Essas dificuldades podem provocar atrasos no atendimento, erros nos valores cobrados, retrabalho dos funcionários e insatisfação dos clientes.

A proposta do sistema é centralizar essas operações em uma aplicação digital, tornando o processo mais eficiente.

## 🚀 Funcionalidades

### 👤 Autenticação e usuários
- Login de usuários.
- Cadastro de funcionários com perfil de atendente.
- Diferenciação de permissões entre administrador e atendente.
- Gerenciamento de informações do perfil.
- Exibição de foto de perfil.

### 🧾 Gerenciamento de comandas
- Abertura de comandas.
- Registro de pedidos e produtos.
- Consulta e acompanhamento das comandas abertas.
- Cálculo automático dos valores.
- Fechamento de comandas.
- Histórico de comandas fechadas.
- Busca e filtros para consulta de registros.

### 🍽️ Cardápio
- Consulta dos produtos disponíveis.
- Gerenciamento de itens do cardápio pelo administrador.

### 📊 Administração
- Acesso a funcionalidades exclusivas do administrador.
- Consulta de informações sobre vendas.
- Acompanhamento de registros e resultados operacionais.

## 🛠️ Tecnologias utilizadas

| Tecnologia | Utilização |
|---|---|
| Python | Desenvolvimento da lógica da aplicação |
| Flet | Construção da interface gráfica |
| Supabase | Serviços de backend e persistência de dados |
| PostgreSQL | Banco de dados relacional |
| Git | Controle de versão |
| GitHub | Hospedagem do código-fonte |
| Android | Plataforma de execução do aplicativo |

## 🏗️ Arquitetura do projeto

O aplicativo utiliza uma organização modular, separando a interface, as regras de funcionamento e a comunicação com o banco de dados.

A interface é desenvolvida com **Flet**, utilizando **Python**, enquanto o **Supabase** disponibiliza os serviços de backend e o banco de dados PostgreSQL.

Essa separação facilita a manutenção do código e a evolução das funcionalidades.

## 👥 Perfis de acesso

**Administrador:** responsável pelo acompanhamento das operações, gerenciamento do cardápio e consulta de informações gerenciais.

**Atendente:** responsável pelas atividades operacionais, incluindo registro de pedidos, acompanhamento e fechamento de comandas.

## 💻 Execução do projeto

### Pré-requisitos

- Python instalado.
- Git instalado.
- Dependências do projeto.
- Configuração de acesso a um projeto Supabase.

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU-USUARIO/pastelaria-gestao-comandas.git
cd pastelaria-gestao-comandas
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

### 3. Ativar o ambiente virtual

No Windows:

```bash
.venv\Scripts\activate
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar o Supabase

Crie um arquivo `.env` na raiz do projeto com as variáveis:

```env
SUPABASE_URL=SUA_URL_PUBLICA
SUPABASE_KEY=SUA_CHAVE_PUBLICAVEL
```

Utilize somente a chave pública destinada ao cliente. Não publique senhas ou chaves administrativas.

O projeto também deve estar associado a um banco de dados Supabase com as tabelas e políticas de acesso necessárias.

### 6. Executar o aplicativo

```bash
python main.py
```

## 📱 Versão Android

O aplicativo também pode ser compilado para Android utilizando o Flet.

Exemplo de comando:

```bash
flet build apk --arch arm64-v8a --yes
```

A compilação requer as ferramentas Android e Flutter configuradas no ambiente de desenvolvimento.

## 📚 Contexto acadêmico

**Curso:** Análise e Desenvolvimento de Sistemas  
**Instituição:** Universidade Cruzeiro do Sul  
**Disciplina:** Projeto de Software e Diagnóstico Comunitário — Experiência Prática I  
**Tipo de projeto:** Produto Mínimo Viável (MVP)  
**Área de aplicação:** Gestão de pequenos estabelecimentos alimentícios

O projeto foi desenvolvido a partir de um diagnóstico realizado com um estabelecimento real, buscando aplicar conhecimentos de análise de requisitos, desenvolvimento de software, banco de dados e construção de interfaces.

## 🔮 Possibilidades de evolução

Entre as funcionalidades que poderão ser incorporadas em versões futuras, destacam-se:

- Controle de estoque.
- Integração com meios de pagamento.
- Relatórios gerenciais avançados.
- Indicadores adicionais de desempenho.
- Melhorias contínuas de usabilidade e segurança.

## 👨‍💻 Autor

**Matheus Santos Vieira**  
Graduando em Análise e Desenvolvimento de Sistemas — Universidade Cruzeiro do Sul.

Projeto desenvolvido para fins acadêmicos.