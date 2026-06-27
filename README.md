Sistema de Diagnóstico Automotivo OBD-II

Sistema web desenvolvido em Python + Django para auxiliar oficinas mecânicas na interpretação de códigos de falha OBD-II utilizando modelos de IA.

O usuário informa os dados do veículo e os códigos de falha, e o sistema gera um diagnóstico técnico detalhado, além de um laudo profissional em HTML e PDF.

Principais funcionalidades
Diagnóstico de códigos OBD-II com apoio de IA
Interface web desenvolvida em Django
Histórico de diagnósticos
Geração de relatórios em HTML e PDF
Personalização dos laudos com os dados da oficina
Validação automática dos códigos informados
Suporte para execução via navegador ou linha de comando (CLI)
Tecnologias utilizadas
Python 3.11+
Django
Bootstrap 5
SQLite
ReportLab
Jinja2
API compatível com OpenAI (OpenAI, NVIDIA NIM, Groq, Together AI, Ollama)
Estrutura do projeto
gerenciador/

├── main.py
├── manage.py
├── ai_client.py
├── diagnostic_service.py
├── report_generator.py
├── pdf_generator.py
├── config.py
│
├── core/
├── web/
├── templates/
├── static/
├── assets/
├── input/
└── output/
Instalação

Clone o projeto:

git clone <repositorio>

cd gerenciador

Crie um ambiente virtual:

python -m venv venv

Windows

venv\Scripts\activate

Linux/Mac

source venv/bin/activate

Instale as dependências:

pip install -r requirements.txt

Execute as migrations:

python manage.py migrate
Configuração

Crie um arquivo .env na raiz do projeto.

BASE_URL=https://integrate.api.nvidia.com/v1

OPENAI_API_KEY=sua_api_key

OPENAI_MODEL=meta/llama-3.1-70b-instruct

Também é possível utilizar outros provedores compatíveis com a API OpenAI, como:

OpenAI
NVIDIA NIM
Groq
Together AI
Ollama
Executando o sistema

Inicie o servidor Django:

python manage.py runserver

Depois acesse:

http://127.0.0.1:8000
Fluxo de utilização
Informe os dados do veículo.
Digite os códigos OBD-II.
Aguarde o processamento da IA.
Visualize o diagnóstico.
Gere o relatório em PDF.
Interface

O sistema possui quatro áreas principais:

Dashboard
Nova análise
Histórico de diagnósticos
Configurações da oficina

Nas configurações é possível definir:

nome da oficina;
endereço;
telefone;
mecânico responsável;
logotipo utilizado nos relatórios.
Logo da oficina

Para utilizar uma logo personalizada, basta colocar um arquivo chamado logo na pasta:

assets/

logo.png
logo.jpg
logo.jpeg
logo.webp

O sistema procura automaticamente pelos formatos acima.

Utilização via CLI

Também é possível executar o sistema pelo terminal.

Diagnóstico simples:

python main.py --codes "P0300,P0171"

Usando um arquivo JSON:

python main.py --file input/example.json

Gerando apenas HTML:

python main.py --codes "P0300" --html-only
Estrutura dos laudos

Cada relatório contém:

informações da oficina;
dados do cliente;
dados do veículo;
resumo executivo;
diagnóstico detalhado de cada código;
recomendações técnicas;
espaço para assinaturas.
Tratamento de erros

O sistema possui tratamento para situações comuns como:

códigos inválidos;
timeout da API;
limite de requisições (retry automático);
falhas de autenticação;
respostas inválidas do modelo de IA.
Deploy

O projeto pode ser publicado em plataformas como:

Railway
Render

Basta configurar as variáveis de ambiente e executar as migrations durante o deploy.

Licença

Projeto desenvolvido para fins de estudo, demonstração e portfólio.
