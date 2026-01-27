# Workflow n8n

Workflow responsável por orquestrar a extração de PDFs via n8n.

## Passos

1. Inicie os serviços com `docker-compose up -d` na raiz do projeto.
2. Acesse `http://localhost:5678/` e importe o arquivo `workflow-n8n.json` desta pasta.
3. Configure a variável de ambiente `EXTRACTOR_URL` para `http://pdf-extractor:8000` nas credenciais globais (já definida por padrão no docker-compose).
4. Posicione os PDFs na pasta `./input_pdfs` da raiz do projeto.
5. Execute o workflow manualmente (nó Manual Trigger).

## O que o workflow faz

- Lê todos os PDFs em `/data/input_pdfs`.
- Converte cada arquivo para base64 e chama `POST /extract` do micro-serviço.
- Normaliza os registros, aplica defaults de nome/códigos e grava dois arquivos:
  - `./output/posicoes.csv`
  - `./output/posicoes.xlsx`
- Em caso de erro de parse, um JSON com detalhes é salvo em `./output/errors/<arquivo>.json`.

O workflow pode ser ajustado para outros bancos adicionando nós ou ajustando o dicionário dentro do nó `Normalize Items`.
