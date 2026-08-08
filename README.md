# PDF to Audio

Extrai texto de PDFs, limpa cabeçalhos/rodapés, divide por capítulos e gera áudio (TTS) por capítulo.

## Funcionalidades

- Extração de texto página a página (PyMuPDF)
- Leitura de TOC/sumário do PDF, quando disponível
- Remoção de linhas repetidas nas bordas (headers/footers)
- Separação em capítulos via TOC (ou capítulo único sem TOC)
- Exportação para `extracted.json` e `chapters.json`
- TTS por capítulo com **edge-tts** (MP3 + playlist `.m3u`)
- CLI (`main.py`) e API HTTP (`server.py`) com upload estilo Postman

## Estrutura

```text
pdfToAudio/
├── app/
│   ├── models.py
│   ├── extract.py
│   ├── cleanup.py
│   ├── chapters.py
│   ├── tts.py         # síntese de áudio por capítulo
│   ├── pipeline.py
│   └── io.py
├── tests/
├── postman/
├── main.py
├── server.py
└── output/            # gerado localmente (gitignored)
```

## Requisitos

- Python 3.9+ (3.12+ recomendado)
- Ambiente virtual recomendado
- Internet para TTS (`edge-tts`)

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Uso (CLI)

Só extrair texto e capítulos:

```bash
python main.py caminho/para/livro.pdf
```

Extrair **e** gerar áudio:

```bash
python main.py livro.pdf --tts
python main.py livro.pdf --tts --voice pt-BR-AntonioNeural
```

Saída padrão:

```text
output/<nome-do-pdf>/extracted.json
output/<nome-do-pdf>/chapters.json
output/<nome-do-pdf>/audio/
  ├── 01-titulo.mp3
  ├── 02-outro.mp3
  └── playlist.m3u
```

Listar vozes em português:

```bash
edge-tts --list-voices | grep pt-BR
```

## Uso no Postman

```bash
python server.py
```

1. Importe `postman/pdf-to-audio.postman_collection.json`
2. **Body** → **form-data** → campo `file` (tipo **File**)
3. Requests:
   - `POST /extract` — só JSON na resposta
   - `POST /extract?save=true` — grava JSON no disco
   - `POST /extract?save=true&tts=true` — JSON + MP3 (pode demorar)

Docs: http://127.0.0.1:8000/docs

## Testes

```bash
# unidade + integração rápida (sem rede)
pytest -v -m "not e2e"

# end-to-end (gera PDF, roda CLI com --tts; precisa de internet)
pytest -v -m e2e
```

## Próximos passos (opcional)

- Exportação M4B com metadados
- Filtro de TOC por nível (`level`) e heurísticas sem sumário
- Jobs em background para TTS na API (evitar timeout em PDFs longos)
