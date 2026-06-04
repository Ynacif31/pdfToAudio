# PDF to Audio

Extrai texto de PDFs, limpa cabeçalhos/rodapés repetidos, divide por capítulos (TOC) e prepara a pipeline para conversão em audiolivro.

## Funcionalidades atuais

- Extração de texto página a página (PyMuPDF)
- Leitura de TOC/sumário do PDF, quando disponível
- Remoção de linhas repetidas nas bordas das páginas (headers/footers)
- Separação em capítulos via TOC (ou capítulo único sem TOC)
- Exportação para `extracted.json` e `chapters.json`
- CLI (`main.py`) e API HTTP (`server.py`) com upload estilo Postman

## Estrutura do projeto

```text
pdfToAudio/
├── app/
│   ├── models.py      # tipos (PageData, ChapterData, …)
│   ├── extract.py     # leitura do PDF (arquivo ou bytes)
│   ├── cleanup.py     # limpeza de headers/footers
│   ├── chapters.py    # divisão por capítulos
│   ├── pipeline.py    # orquestração (CLI + API)
│   └── io.py          # gravação JSON
├── tests/
├── postman/           # collection para testar a API
├── main.py            # entrada CLI
├── server.py          # entrada API (FastAPI)
└── output/            # gerado localmente (gitignored)
```

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

```bash
python main.py caminho/para/livro.pdf
```

Saída padrão:

```text
output/<nome-do-pdf>/extracted.json
output/<nome-do-pdf>/chapters.json
```

Caminho customizado só para `extracted.json` (capítulos ficam na mesma pasta):

```bash
python main.py livro.pdf -o output/meu-livro/extracted.json
```

## Uso no Postman (upload de arquivo)

```bash
python server.py
```

1. Importe `postman/pdf-to-audio.postman_collection.json`
2. Request **Extract PDF (upload file)**
3. **Body** → **form-data** → campo `file` (tipo **File**) → selecione o PDF
4. **Send** → `POST http://127.0.0.1:8000/extract`

Gravar JSON no disco do servidor: `POST /extract?save=true` → cria `extracted.json` e `chapters.json` em `output/<nome-do-pdf>/`.

Documentação interativa: http://127.0.0.1:8000/docs

## Testes

```bash
pytest -v
```

## Próximos passos

- Geração de áudio com TTS (por capítulo)
- Metadados e exportação como audiolivro (M4B / playlist)
- Filtro de TOC por nível (`level`) e heurísticas sem sumário
