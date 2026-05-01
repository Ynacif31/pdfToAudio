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

## Uso

Coloque o PDF na raiz do projeto e ajuste o nome no arquivo `extract_pdf.py`.

```bash
python extract_pdf.py
```

O JSON extraído será salvo em:

```bash
output/extracted.json
```

## Próximos passos

- Limpeza de cabeçalhos e rodapés
- Separação automática por capítulos
- Geração de áudio com TTS
- Exportação como audiolivro