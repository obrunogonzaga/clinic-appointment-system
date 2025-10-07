# PDF Investment Extractor

Este micro-serviço FastAPI recebe relatórios em PDF de diferentes bancos brasileiros e converte as tabelas de posição em um layout padronizado.

## Requisitos

- Python 3.11+
- Dependências listadas em `requirements.txt`
- Tesseract OCR (opcional, instalado automaticamente via Dockerfile)

## Como executar localmente

```bash
cd extractor
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API ficará disponível em `http://localhost:8000`.

### Endpoints

- `GET /health`: verificação simples de status.
- `POST /extract`: recebe um JSON com o arquivo em base64 e retorna os itens extraídos. Exemplo de payload:

```json
{
  "filename": "relatorio.pdf",
  "file_b64": "<BASE64>",
  "bank_hint": "auto",
  "return_format": "json",
  "enrichment": { "try_cnpj_match": true }
}
```

Quando `return_format` for `csv`, o campo `csv` da resposta conterá o arquivo completo.

## Estrutura do projeto

- `main.py`: aplicação FastAPI.
- `parsers/`: implementações específicas por banco (Itaú, XP, Bradesco, BTG).
- `utils/`: utilitários de normalização e enriquecimento.
- `data/`: arquivos auxiliares (`base_clientes.csv`, `cnpj_map.csv`).
- `tests/`: testes unitários com PDFs sintéticos para cada banco.

## Testes

```bash
cd extractor
pytest
```

Os arquivos de amostra estão em `tests/samples/`. Para adicionar novos bancos, crie uma classe em `parsers/` que herde de `BaseParser` e registre em `parsers/__init__.py`.
