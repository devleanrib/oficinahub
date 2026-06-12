# Sistema de Diagnostico Automotivo OBD-II

Sistema completo de diagnostico automotivo que recebe codigos de falha OBD-II e informacoes do veiculo, consulta um modelo de IA para gerar analises tecnicas e produz laudos profissionais em HTML e PDF.

## Visao Geral

O sistema permite:
- Receber codigos de falha OBD-II e informacoes do veiculo via web, CLI interativo, argumentos ou arquivos
- Consultar IA para gerar diagnosticos tecnicos completos com contexto do veiculo
- Produzir laudos profissionais em HTML e PDF
- Layout profissional para clientes de oficina
- Validar e normalizar codigos de entrada
- Tratar erros de API com retry automatico
- Interface web responsiva com Bootstrap 5
- Historico de diagnosticos persistidos

## Arquitetura

```
gerenciador/
│
├── main.py                 # Ponto de entrada CLI
├── ai_client.py            # Cliente para comunicacao com IA
├── diagnostic_service.py   # Servico de diagnostico
├── report_generator.py     # Preparacao de dados do relatorio
├── pdf_generator.py        # Geracao de HTML e PDF
├── models.py               # Modelos de dados (dataclasses)
├── prompts.py              # Prompts centralizados
├── config.py               # Configuracoes do sistema
├── requirements.txt        # Dependencias
├── manage.py               # Django manage.py
├── db.sqlite3              # Banco de dados SQLite
│
├── core/                   # Configuracao Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── web/                    # App Django (Interface Web)
│   ├── models.py           # Models Django (Diagnosis, ShopSettings)
│   ├── views.py            # Views Django
│   ├── urls.py             # URLs da web
│   ├── context_processors.py
│   ├── templates/web/      # Templates Django + Bootstrap 5
│   └── static/web/         # CSS/JS customizados
│
├── assets/                 # Imagens da oficina
│   └── logo.png            # Logo automatica (png/jpg/jpeg/webp)
│
├── templates/              # Templates Jinja2 (PDF)
│   ├── base.html
│   └── client_report.html
│
├── static/                 # Arquivos estaticos (PDF)
│   └── style.css
│
├── input/                  # Arquivos de entrada
│   └── example.json
│
└── output/                 # Laudos gerados
    ├── laudo_*.html
    └── laudo_*.pdf
```

## Pre-requisitos

- Python 3.11+
- API Key de provedor de IA (OpenAI, NVIDIA, Groq, etc.)

## Instalacao

1. Acesse o diretorio do projeto:
```bash
cd gerenciador
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependencias:
```bash
pip install -r requirements.txt
```

4. Execute as migrations do banco:
```bash
python manage.py migrate
```

## Configuracao

1. Crie um arquivo `.env` na raiz do projeto:
```env
# URL base do provedor de IA
BASE_URL=https://integrate.api.nvidia.com/v1

# Chave da API
OPENAI_API_KEY=sua-chave-aqui

# Modelo a ser utilizado
OPENAI_MODEL=meta/llama-3.1-70b-instruct
```

2. Ou defina as variaveis de ambiente:
```bash
export BASE_URL="https://integrate.api.nvidia.com/v1"
export OPENAI_API_KEY="sua-chave-aqui"
```

### Configuracoes Disponiveis

| Variavel | Padrao | Descricao |
|----------|--------|-----------|
| `BASE_URL` | `https://api.openai.com/v1` | URL base do provedor de IA |
| `OPENAI_API_KEY` | (obrigatorio) | Chave da API do provedor |
| `OPENAI_MODEL` | `gpt-4` | Modelo a ser utilizado |
| `OPENAI_TEMPERATURE` | `0.1` | Temperatura (0.0-1.0) |
| `OPENAI_MAX_TOKENS` | `3000` | Limite de tokens |
| `OPENAI_TIMEOUT` | `60` | Timeout em segundos |
| `MAX_RETRIES` | `3` | Tentativas maximas |
| `LOG_LEVEL` | `DEBUG` | Nivel de logging |

### Provedores Suportados

- **OpenAI**: `https://api.openai.com/v1`
- **NVIDIA NIM**: `https://integrate.api.nvidia.com/v1`
- **Groq**: `https://api.groq.com/openai/v1`
- **Together AI**: `https://api.together.xyz/v1`
- **Local (Ollama)**: `http://localhost:11434/v1`

## Interface Web (Recomendada)

A interface web e a principal forma de utilizacao do sistema. Ela oferece um fluxo guiado passo a passo.

### Iniciar o Servidor

```bash
python manage.py runserver
```

Acesse no navegador: `http://127.0.0.1:8000`

### Paginas Disponiveis

| URL | Descricao |
|-----|-----------|
| `/` | Dashboard com estatisticas e acesso rapido |
| `/analise/` | Wizard de 3 etapas para novo diagnostico |
| `/historico/` | Lista de todos os diagnosticos realizados |
| `/configuracoes/` | Dados da oficina e configuracoes |

### Fluxo da Analise

**Etapa 1 - Dados do Veiculo:**
- Preencha marca, modelo, ano, motorizacao, combustivel
- Campos opcionais: transmissao, quilometragem, placa
- Clique em "Proximo"

**Etapa 2 - Codigos OBD-II:**
- Digite os codigos separados por virgula
- Exemplo: `P0300,P0171,U0100`
- Clique em "Analisar"

**Etapa 3 - Confirmacao:**
- Revise os dados do veiculo e codigos
- Clique em "Confirmar e Analisar"
- Aguarde o processamento da IA

**Resultado:**
- Resumo executivo com criticidade geral
- Lista detalhada de cada diagnostico
- Causas, riscos e recomendacoes por codigo
- Botao para gerar PDF do relatorio

### Configuracoes da Oficina

Acesse `/configuracoes/` para configurar:
- Nome da oficina
- Endereco e telefone
- Mecanico responsavel e credencial
- Logo (detectada automaticamente de `assets/`)

Essas informacoes sao utilizadas automaticamente nos relatorios PDF.

## Modo CLI

O sistema tambem pode ser utilizado via linha de comando:

### Modo Interativo
```bash
python main.py
```

### Modo CLI com Codigos
```bash
python main.py --codes "P0300,P0171,U0100"
```

### Modo CLI com Arquivo
```bash
python main.py --file input/example.json
```

### Gerar Apenas HTML
```bash
python main.py --codes "P0300" --html-only
```

## Logo da Oficina

O sistema detecta automaticamente a logo da oficina para inserir no cabecalho do laudo.

Para adicionar sua logo, coloque um arquivo chamado `logo` na pasta `assets/`:

```
assets/
├── logo.png      (prioridade 1)
├── logo.jpg      (prioridade 2)
├── logo.jpeg     (prioridade 3)
└── logo.webp     (prioridade 4)
```

O sistema procura os arquivos nesta ordem e utiliza o primeiro encontrado. Se nenhum arquivo existir, o relatorio e gerado normalmente sem a logo.

**Para trocar a logo:** basta substituir o arquivo na pasta `assets/`. Nenhuma alteracao no codigo e necessaria.

## Estrutura do Laudo

O laudo profissional inclui:

1. **Cabecalho** - Logo e dados da oficina
2. **Dados do Cliente** - Nome, documento, telefone
3. **Dados do Veiculo** - Marca, modelo, ano, motorizacao, combustivel, transmissao, quilometragem, placa
4. **Resumo Executivo** - Quantidade de falhas e criticidade
5. **Diagnosticos** - Cada codigo com causas, riscos e recomendacoes
6. **Conclusao** - Orientacao ao cliente
7. **Assinaturas** - Espaco para mecanico e cliente

## Estrutura de Codigos OBD-II

- **P** (Powertrain): Motor, transmissao, emissoes (ex: P0300)
- **C** (Chassis): ABS, suspensao, direcao, freios (ex: C0035)
- **B** (Body): Airbag, cintos, carroceria (ex: B0020)
- **U** (Network): Comunicacao entre modulos (ex: U0100)

## Estrutura do Codigo

| Arquivo | Responsabilidade |
|---------|------------------|
| `config.py` | Configuracoes do sistema |
| `models.py` | Modelos de dados (dataclasses) |
| `prompts.py` | Prompts da IA |
| `ai_client.py` | Comunicacao com IA |
| `diagnostic_service.py` | Orquestracao do diagnostico |
| `report_generator.py` | Preparacao de dados |
| `pdf_generator.py` | Geracao de HTML e PDF |
| `core/settings.py` | Configuracoes Django |
| `web/models.py` | Models Django (Diagnosis, ShopSettings) |
| `web/views.py` | Views Django (dashboard, analise, resultado, historico, configuracoes) |
| `web/urls.py` | Roteamento URL |
| `web/templates/` | Templates Django + Bootstrap 5 |
| `main.py` | Interface CLI |

## Tratamento de Erros

- **Rate Limit**: Retry com backoff exponencial
- **Timeout**: Retry automatico
- **Autenticacao**: Mensagem clara sobre API Key
- **Codigos invalidos**: Validacao de formato
- **Respostas malformadas**: Validacao de JSON

## Licenca

Projeto para fins educacionais e de demonstracao.
