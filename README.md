# PDF to Audio

Projeto inicial para extrair texto de PDFs e preparar uma pipeline para conversão em audiolivro.

## Funcionalidades atuais

- Extração de texto página a página
- Leitura de TOC/sumário do PDF, quando disponível
- Exportação do conteúdo extraído para JSON

## Requisitos

- Python 3.12+
- Ambiente virtual recomendado

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Uso (linha de comando)

Passe o caminho do PDF como argumento:

```bash
python main.py caminho/para/livro.pdf
```

Saída padrão (por nome do arquivo):

```bash
output/<nome-do-pdf>/extracted.json
```

Caminho de saída customizado:

```bash
python main.py livro.pdf -o output/meu-livro.json
```

## Uso no Postman (upload de arquivo)

O Postman envia arquivos em requisições HTTP. Suba a API local, depois anexe o PDF como no Postman:

```bash
pip install -r requirements.txt
python server.py
```

1. Importe a collection: `postman/pdf-to-audio.postman_collection.json`
2. Request **Extract PDF (upload file)**
3. Aba **Body** → **form-data**
4. Campo `file` → tipo **File** → escolha o `.pdf`
5. **Send**

URL: `POST http://127.0.0.1:8000/extract`

Para gravar JSON no disco do servidor: `POST /extract?save=true`

Documentação interativa: http://127.0.0.1:8000/docs

Script legado na raiz (`extract_pdf.py`) ainda existe; prefira `main.py` (CLI) ou `server.py` (Postman).

## Próximos passos

- Limpeza de cabeçalhos e rodapés
- Separação automática por capítulos
- Geração de áudio com TTS
- Exportação como audiolivro