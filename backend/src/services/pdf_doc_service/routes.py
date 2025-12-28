from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from .adobe_client import upload_pdf, convert_to_docx, download_docx

router = APIRouter(prefix="/pdf", tags=["PDF Conversion"])


@router.post("/to-docx")
def pdf_to_docx(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    pdf_bytes = file.file.read()

    asset_id = upload_pdf(pdf_bytes)
    download_url = convert_to_docx(asset_id)
    docx_bytes = download_docx(download_url)

    return StreamingResponse(
        iter([docx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=output.docx"}
    )
