# Sistema de Diagnóstico Automotivo OBD-II

Sistema completo de diagnóstico automotivo que recebe códigos de falha OBD-II, consulta um modelo de IA (OpenAI GPT-4) para gerar análises técnicas detalhadas e produz um relatório profissional em Markdown.

## Visão Geral

O sistema permite:
- Receber códigos de falha OBD-II via CLI interativo, argumentos de linha de comando ou arquivos (JSON/TXT)
- Consultar IA para gerar diagnósticos técnicos completos
- Produzir relatórios Markdown profissionais com layout padronizado
- Validar e normalizar códigos de entrada
- Tratar erros de API com retry automático

## Arquitetura

```
obd2_diagnostic/
│
├── main.py                 # Ponto de entrada da aplicação
├── ai_client.py            # Cliente para comunicação com OpenAI
├── diagnostic_service.py   # Serviço de diagnóstico (orchestration)
├── report_generator.py     # Gerador de relatório Markdown
├── models.py               # Modelos de dados (dataclasses)
├── prompts.py              # Prompts centralizados
├── config.py               # Configurações do sistema
├── requirements.txt        # Dependências
│
├── input/                  # Diretório para arquivos de entrada
│   └── example.json        # Exemplo de entrada JSON
│
└── output/                 # Diretório para relatórios gerados
```

## Pré-requisitos

- Python 3.11+
- API Key da OpenAI

## Instalação

1. Clone ou copie o projeto:
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

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Configuração

1. Crie um arquivo `.env` na raiz do projeto:
```env
# URL base do provedor de IA (obrigatório se não for OpenAI)
BASE_URL=https://integrate.api.nvidia.com/v1

# Chave da API (obrigatório)
OPENAI_API_KEY=sua-chave-aqui

# Modelo a ser utilizado (opcional)
OPENAI_MODEL=meta/llama-3.1-70b-instruct

# Outras configurações opcionais
LOG_LEVEL=DEBUG
```

2. Ou defina as variáveis de ambiente:
```bash
export BASE_URL="https://integrate.api.nvidia.com/v1"
export OPENAI_API_KEY="sua-chave-aqui"
```

### Configurações Disponíveis

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `BASE_URL` | `https://api.openai.com/v1` | URL base do provedor de IA |
| `OPENAI_API_KEY` | (obrigatório) | Chave da API do provedor |
| `OPENAI_MODEL` | `gpt-4` | Modelo a ser utilizado |
| `OPENAI_TEMPERATURE` | `0.1` | Temperatura (0.0-1.0) |
| `OPENAI_MAX_TOKENS` | `3000` | Limite de tokens |
| `OPENAI_TIMEOUT` | `60` | Timeout em segundos |
| `MAX_RETRIES` | `3` | Tentativas máximas |
| `LOG_LEVEL` | `DEBUG` | Nível de logging |

### Provedores Suportados

O sistema utiliza a biblioteca `openai` que é compatível com qualquer provedor que implemente a API OpenAI. Exemplos:

- **OpenAI**: `BASE_URL=https://api.openai.com/v1`
- **NVIDIA NIM**: `BASE_URL=https://integrate.api.nvidia.com/v1`
- **Groq**: `BASE_URL=https://api.groq.com/openai/v1`
- **Together AI**: `BASE_URL=https://api.together.xyz/v1`
- **Local (Ollama)**: `BASE_URL=http://localhost:11434/v1`

## Uso

### Modo Interativo

```bash
python main.py
```

Ou explicitamente:

```bash
python main.py --interactive
```

O modo interativo apresenta um menu com opções:
1. Digitar códigos manualmente
2. Ler de arquivo
3. Sair

### Modo CLI com Códigos

```bash
python main.py --codes "P0300,P0171,U0100"
```

### Modo CLI com Arquivo

```bash
python main.py --file input/example.json
```

### Formato dos Arquivos de Entrada

**Arquivo JSON:**
```json
{
  "codes": [
    "P0300",
    "P0171",
    "U0100"
  ]
}
```

**Arquivo TXT:**
```
P0300
P0171
U0100
```

### Especificar Arquivo de Saída

```bash
python main.py --codes "P0300" --output meu_relatorio.md
```

## Exemplo de Saída

O relatório gerado segue sempre o mesmo layout:

```markdown
# Relatório de Diagnóstico Automotivo

**Data/Hora de Geração:** 2026-06-11 10:30:00

**Quantidade de Códigos Analisados:** 3

**Criticidade Geral:** Alta

## Resumo Executivo

Foram analisados 3 codigo(s) de falha OBD-II. 1 codigo(s) com criticidade alta.
...

---

## Código P0300

### Significado

Falha de combustão aleatória detectada

### Descrição Técnica

O código P0300 indica que o módulo de controle do motor (ECM) detectou ...

### Possíveis Causas

- Bobina de ignição com mau funcionamento
- Vela de ignição contaminada ou desgastada
- ...

### Sintomas

- Motor oscilando em marcha lenta
- Perda de potência
- ...

### Impactos

- Aumento do consumo de combustível
- Risco de danos ao catalisador
- ...

### Criticidade

🟠 **Alta**

### Recomendações

- Verificar códigos de freeze frame
- ...

### Ações Corretivas

- Substituir velas de ignição
- ...

### Operacionalidade

✅ O veículo pode continuar em operação
...

---

## Conclusão

ATENÇÃO REQUERIDA: 1 codigo(s) de alta criticidade (P0300)...
```

## Estrutura de Códigos OBD-II

O sistema aceita códigos nos seguintes formatos:
- **P** (Powertrain): Motor, transmissão, emissões (ex: P0300)
- **C** (Chassis): ABS, suspensão, direção, freios (ex: C0035)
- **B** (Body): Airbag, cintos, carroceria (ex: B0020)
- **U** (Network): Comunicação entre módulos (ex: U0100)

## Tratamento de Erros

O sistema trata automaticamente:
- **Rate Limit**: Retry com backoff exponencial
- **Timeout**: Retry automático
- **Autenticação**: Mensagem clara sobre API Key
- **Códigos inválidos**: Validação de formato
- **Respostas malformadas**: Validação de JSON

## Desenvolvimento

### Estrutura do Código

| Arquivo | Responsabilidade |
|---------|------------------|
| `config.py` | Configurações do sistema |
| `models.py` | Modelos de dados (dataclasses) |
| `prompts.py` | Prompts da IA centralizados |
| `ai_client.py` | Comunicação com OpenAI |
| `diagnostic_service.py` | Orquestração do diagnóstico |
| `report_generator.py` | Geração de relatório Markdown |
| `main.py` | Interface do usuário |

### Adicionar Novos Provedores de IA

O sistema é compatível com qualquer provedor que implemente a API OpenAI. Basta alterar as variáveis `BASE_URL` e `OPENAI_API_KEY` no arquivo `.env`:

```env
# Exemplo com NVIDIA NIM
BASE_URL=https://integrate.api.nvidia.com/v1
OPENAI_API_KEY=nvapi-sua-chave
OPENAI_MODEL=meta/llama-3.1-70b-instruct
```

```env
# Exemplo com Groq
BASE_URL=https://api.groq.com/openai/v1
OPENAI_API_KEY=gsk_sua-chave
OPENAI_MODEL=llama-3.1-70b-versatile
```

```env
# Exemplo com Ollama (local)
BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama3
```

## Licença

Projeto para fins educacionais e de demonstração.