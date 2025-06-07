# 🛠️ TT Soluções – Plataforma Institucional

Este repositório contém o código-fonte da plataforma web da **TT Soluções**, uma empresa focada em elevar a maturidade tecnológica de pequenas e médias empresas por meio de diagnósticos, suporte técnico e gestão de soluções.

---

## 📚 Sumário

- [🚀 Visão Geral](#visão-geral)
- [🔗 Rotas](#rotas)
  - [Públicas](#rotas-públicas)
  - [Privadas](#rotas-privadas)
- [⚙️ Stack Tecnológica](#stack-tecnológica)
- [🗂️ Estrutura de Pastas](#estrutura-de-pastas)
- [🧪 Como Rodar Localmente](#como-rodar-localmente)
- [📁 Organização de Dados](#organização-de-dados)
- [📌 Observações](#observações)

---

## 🚀 Visão Geral

A plataforma oferece duas áreas principais:

- **Área pública:** onde visitantes podem acessar informações institucionais, preencher um pré-diagnóstico gratuito e visualizar feedbacks de outros usuários.
- **Área privada:** ambiente logado para colaboradores e clientes da TT Soluções, com dashboards de gestão, suporte, projetos e controle de usuários.

---

## 🔗 Rotas

### Rotas Públicas

| Rota                        | Função                                                                                                                    |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `/index`                    | Página inicial pública – Home institucional da TT Soluções (identidade, missão, serviços)                                |
| `/saiba_mais`               | Sobre a empresa – Detalhamento da proposta, valores e modelo de negócio                                                  |
| `/detalhes_pre_diagnostico`| Explicação do pré-diagnóstico – Detalhamento da metodologia e fluxo                                                      |
| `/pre_diagnostico`         | Formulário com 6 eixos de avaliação + dados pessoais e proposta final                                                    |
| `/feedbacks`               | Feedbacks públicos + formulário para envio de novos                                                                      |
| `/login`                   | Tela de autenticação para acesso à área privada                                                                          |

### Rotas Privadas

| Rota                         | Função                                                                                         |
| ---------------------------- | ---------------------------------------------------------------------------------------------- |
| `/index`                     | Descritivo interno do colaborador ou cliente (painel inicial)                                |
| `Pré diagnóstico`            | Visualização interna do formulário (semelhante ao público)                                   |
| `Feedbacks`                  | Visualização interna dos feedbacks (semelhante ao público)                                   |
| `Gerenciar Pré Diagnósticos` | Administração dos dados coletados – ver, editar, exportar                                    |
| `Gerenciar Feedbacks`        | Moderação e análise dos feedbacks recebidos                                                  |
| `Gerenciar Suporte`          | Gestão dos chamados e tickets técnicos                                                       |
| `Gerenciar Usuários`         | Criação e controle de permissões e perfis de colaboradores                                   |
| `Projetos`                   | Monitoramento e gestão de projetos internos/externos                                         |
| `Suporte`                    | Canal para abertura de chamados por usuários (cliente e colaborador)                         |
| `Perfil`                     | Dados pessoais e configurações de conta                                                      |
| `Sair`                       | Logout                                                                                       |

---

## ⚙️ Stack Tecnológica

- **Front-end:** HTML, CSS, JavaScript
- **Back-end:** Python + Flask
- **Banco de Dados:** PostgreSQL (Render)
- **Data Lake:** Estrutura em SQL, com organização por entrada, saída e base
- **Hospedagem:** Render
- **Controle de versão:** Git + GitHub

---

## 🗂️ Estrutura de Pastas

```

tt\_solucoes/
├── api/                      # Lógica de backend (módulos e rotas da API)
│   ├── routes/               # Arquivos de roteamento Flask (API)
│   └── utils/                # Funções auxiliares
├── app/                      # Camada web da aplicação
│   ├── routes/               # Arquivos de roteamento Flask
│   ├── static/               # Arquivos estáticos (CSS, JS, imagens)
│   ├── templates/            # Templates HTML com uso de Jinja
│   │   ├── pages/            # Páginas públicas e privadas
│   │   ├── components/       # Componentes reutilizáveis
│   │   └── macros/           # Macros Jinja para reutilização lógica
│   └── utils/                # Funções auxiliares
├── config/                   # Configuração de banco de dados, autenticação, modelos
├── data/                     # Entrada, saída e base de dados locais
├── logs/                     # Logs da aplicação
├── temp/                     # Arquivos temporários
├── tests/                    # Scripts de testes automatizados (WIP)
├── utils/                    # Módulos reutilizáveis por domínio (ex: pré-diagnóstico, usuários)
├── run.py                    # Arquivo principal de execução da aplicação
└── requirements.txt          # Lista de dependências Python

````

---

## 🧪 Como Rodar Localmente

1. **Clone o repositório:**

    ```bash
   git clone https://github.com/seu-usuario/tt_solucoes.git
   cd tt_solucoes
    ```

2. **Crie um ambiente virtual (opcional, mas recomendado):**

    ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   .\venv\Scripts\activate    # Windows
    ```

3. **Instale as dependências:**

    ```bash
   pip install -r requirements.txt
    ```

4. **Execute a aplicação:**

   ```bash
   python run.py
   ```

5. **Acesse no navegador:**

   ```
   http://localhost:5000
   ```

---

## 📁 Organização de Dados

* **`data/base`** – estrutura principal de dados utilizados na aplicação
* **`data/entrada`** – dados coletados do usuário (ex: formulários)
* **`data/saida`** – relatórios e propostas geradas pela plataforma

---

## 📌 Observações

* A aplicação está em constante evolução e segue os princípios de: clareza, eficiência, sustentabilidade e ética técnica.
* A área privada será futuramente segmentada por permissões (diretores, analistas, etc.).
* Documentações internas estão sendo mantidas via HackMD e podem futuramente integrar diretamente ao painel.

---

> Desenvolvido com 💡 por TT Soluções – transformando tecnologia em solução prática.
