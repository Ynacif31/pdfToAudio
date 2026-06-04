from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse

from app.io import default_chapters_path, default_output_path, save_chapters_to_json, save_to_json
from app.pipeline import (
    PipelineResult,
    pipeline_result_to_dict,
    process_pdf_upload,
)

app = FastAPI(
    title="PDF to Audio API",
    description="Upload a PDF (multipart form field `file`) — same as attaching a file in Postman.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract")
async def extract_endpoint(
    file: UploadFile = File(..., description="PDF file (form-data, type File)"),
    save: bool = Query(
        False,
        description="If true, writes output/<pdf-name>/extracted.json and chapters.json on disk",
    ),
) -> JSONResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Upload a .pdf file in the `file` field")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        result = process_pdf_upload(data, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {exc}") from exc

    payload = pipeline_result_to_dict(result)
    if save:
        payload["saved_to"] = _save_result(result)

    return JSONResponse(content=payload)


def _save_result(result: PipelineResult) -> dict[str, str]:
    pdf_ref = Path(result.extracted.file_name)
    extracted_path = default_output_path(pdf_ref)
    chapters_path = default_chapters_path(pdf_ref)
    save_to_json(result.extracted, str(extracted_path))
    save_chapters_to_json(result.chapters, str(chapters_path))
    return {
        "extracted": str(extracted_path.resolve()),
        "chapters": str(chapters_path.resolve()),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
