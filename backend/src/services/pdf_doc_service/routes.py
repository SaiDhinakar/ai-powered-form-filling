import os
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


@router.post("/fill-form")
def fill_pdf_route(form_data: dict):
    # For demonstration, we'll use the sample3.pdf located in the same directory
    # In a real app, this might come from an upload or a specific template ID
    input_pdf = os.path.join(os.path.dirname(__file__), "sample3.pdf")
    output_pdf = os.path.join(os.path.dirname(__file__), "filled_response.pdf")
    
    try:
        from .auto_fill import fill_pdf_form
        output_path = fill_pdf_form(input_pdf, output_pdf, form_data)
        
        return StreamingResponse(
            open(output_path, "rb"),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=filled_form.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
