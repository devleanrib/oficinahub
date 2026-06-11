# Sistema de Diagnostico Automotivo OBD-II

Sistema completo de diagnostico automotivo que recebe codigos de falha OBD-II e informacoes do veiculo, consulta um modelo de IA para gerar analises tecnicas e produz laudos profissionais em HTML e PDF.

## Visao Geral

O sistema permite:
- Receber codigos de falha OBD-II e informacoes do veiculo via CLI interativo, argumentos ou arquivos (JSON/TXT)
- Consultar IA para gerar diagnosticos tecnicos completos com contexto do veiculo
- Produzir laudos profissionais em HTML e PDF
- Layout profissional para clientes de oficina
- Validar e normalizar codigos de entrada
- Tratar erros de API com retry automatico

## Arquitetura

```
gerenciador/
│
├── main.py                 # Ponto de entrada
├── ai_client.py            # Cliente para comunicacao com IA
├── diagnostic_service.py   # Servico de diagnostico
├── report_generator.py     # Preparacao de dados do relatorio
├── pdf_generator.py        # Geracao de HTML e PDF
├── models.py               # Modelos de dados
├── prompts.py              # Prompts centralizados
├── config.py               # Configuracoes do sistema
├── requirements.txt        # Dependencias
│
├── templates/              # Templates Jinja2
│   ├── base.html           # Template base
│   └── client_report.html  # Template do laudo
│
├── static/                 # Arquivos estaticos
│   └── style.css           # CSS profissional
│
├── input/                  # Arquivos de entrada
│   └── example.json        # Exemplo
│
└── output/                 # Laudos gerados
    ├── laudo_*.html        # HTML gerado
    └── laudo_*.pdf         # PDF gerado
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

## Uso

### Modo Interativo (Recomendado)

O modo interativo guia o usuario passo a passo, coletando dados do veiculo antes dos codigos de falha:

```bash
python main.py
```

**Fluxo completo:**

```
=========================================
  SISTEMA DE DIAGNOSTICO AUTOMATIVO OBD-II
=========================================

Informe os dados do veiculo.

Marca: Volkswagen
Modelo: Gol
Ano: 2019
Motorizacao: 1.6 MSI
Combustivel: Flex
Transmissao: Manual
Quilometragem: 85000
Placa (opcional): ABC1D23

=========================================
  DADOS DO VEICULO
=========================================
  Marca:         Volkswagen
  Modelo:        Gol
  Ano:           2019
  Motor:         1.6 MSI
  Combustivel:   Flex
  Transmissao:   Manual
  Quilometragem: 85.000 km
  Placa:         ABC1D23
=========================================

Os dados estao corretos?
  1 - Sim
  2 - Corrigir

Selecione: 1

Informe os codigos encontrados.
Digite separados por virgula.
Exemplo: P0300,P0171,U0100

Codigos: P0300,P0171,U0100

=========================================
  RESUMO DO DIAGNOSTICO
=========================================

  VEICULO:
    Volkswagen Gol 2019

  CODIGOS (3):
    P0300
    P0171
    U0100

=========================================

Confirmar geracao do diagnostico?
  1 - Gerar
  2 - Cancelar

Selecione: 1

Processando 3 codigo(s): P0300, P0171, U0100
Consultando IA... Aguarde.

Laudo gerado com sucesso!
HTML: output/laudo_20260611_192621.html
PDF: output/laudo_20260611_192621.pdf
Criticidade geral: Alta
```

**Recursos do modo interativo:**
- Coleta guiada dos dados do veiculo (8 campos)
- Campo placa opcional (Enter em branco para pular)
- Opcao de corrigir dados antes de prosseguir
- Validacao dos codigos OBD-II
- Resumo final antes de gerar o diagnostico
- Confirmacao antes de consultar a IA
- Opcao de realizar novo diagnostico apos o primeiro

### Modo CLI com Codigos

```bash
python main.py --codes "P0300,P0171,U0100"
```

### Modo CLI com Arquivo

```bash
python main.py --file input/example.json
```

### Gerar Apenas HTML (sem PDF)

```bash
python main.py --codes "P0300" --html-only
```

### Formato dos Arquivos de Entrada

**Arquivo JSON com dados do veiculo:**
```json
{
  "vehicle": {
    "brand": "Volkswagen",
    "model": "Gol",
    "year": "2019",
    "engine": "1.6 MSI",
    "fuel": "Flex",
    "transmission": "Manual",
    "mileage": 85000,
    "plate": "ABC1D23"
  },
  "codes": ["P0300", "P0171", "U0100"]
}
```

**Arquivo JSON apenas codigos:**
```json
{
  "codes": ["P0300", "P0171", "U0100"]
}
```

**Arquivo TXT:**
```
P0300
P0171
U0100
```

### Campos do Veiculo

| Campo | Obrigatorio | Descricao |
|-------|-------------|-----------|
| `brand` | Sim | Marca do veiculo |
| `model` | Sim | Modelo do veiculo |
| `year` | Sim | Ano do veiculo |
| `engine` | Sim | Motorizacao (ex: 1.6 MSI) |
| `fuel` | Sim | Tipo de combustivel |
| `transmission` | Nao | Tipo de transmissao |
| `mileage` | Nao | Quilometragem atual |
| `plate` | Nao | Placa do veiculo |

## Personalizacao do Laudo

### Dados da Oficina

Edite `main.py` ou crie um arquivo de configuracao para definir:

```python
from report_generator import ReportGenerator, ReportMetadata

metadata = ReportMetadata(
    shop_name="Minha Oficina",
    shop_address="Rua X, 123",
    shop_phone="(11) 3456-7890",
    mechanic_name="Joao Mecanico",
    mechanic_credential="CTPS 12345",
)

reporter = ReportGenerator(metadata)
```

### Templates

O sistema utiliza Jinja2 para templates. Para criar um novo template:

1. Crie um arquivo em `templates/`
2. Estenda `base.html`
3. Use o bloco `{% block content %}`
4. Acesse os dados via `{{ variavel }}`

### CSS

O CSS esta em `static/style.css`. Personalize cores, fontes e espacamentos conforme a identidade visual da oficina.

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

## Informacoes do Veiculo

O sistema suporta informacoes detalhadas do veiculo para contextualizar o diagnostico:

```json
{
  "vehicle": {
    "brand": "Volkswagen",
    "model": "Gol",
    "year": "2019",
    "engine": "1.6 MSI",
    "fuel": "Flex",
    "transmission": "Manual",
    "mileage": 85000,
    "plate": "ABC1D23"
  }
}
```

Essas informacoes sao utilizadas pela IA para gerar diagnosticos mais contextualizados e aparecem na secao "DADOS DO VEICULO" do laudo.

## Tratamento de Erros

- **Rate Limit**: Retry com backoff exponencial
- **Timeout**: Retry automatico
- **Autenticacao**: Mensagem clara sobre API Key
- **Codigos invalidos**: Validacao de formato
- **Respostas malformadas**: Validacao de JSON

## Estrutura do Codigo

| Arquivo | Responsabilidade |
|---------|------------------|
| `config.py` | Configuracoes do sistema |
| `models.py` | Modelos de dados (VehicleInfo, DiagnosticResult, DiagnosticReport, InputData) |
| `prompts.py` | Prompts da IA |
| `ai_client.py` | Comunicacao com IA |
| `diagnostic_service.py` | Orquestracao do diagnostico |
| `report_generator.py` | Preparacao de dados |
| `pdf_generator.py` | Geracao de HTML e PDF |
| `templates/` | Templates Jinja2 |
| `static/` | CSS e estaticos |
| `main.py` | Interface do usuario |

## Preparacao para Evolucao

A arquitetura permite futuramente:
- Templates diferentes (Cliente, Tecnico, Premium)
- Insercao de fotos
- QR Code
- Checklist
- Orcamento
- Historico do veiculo
- Personalizacao com identidade visual
- Multiplos temas
- Portal do cliente
- Envio por e-mail
- Dados do veiculo mais detalhados (versao do motor, potencia, etc.)

## Licenca

Projeto para fins educacionais e de demonstracao.