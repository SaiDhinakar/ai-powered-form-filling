import os
import sys
from adobe_client import upload_pdf, convert_to_docx, download_docx

def verify_conversion():
    # Use one of the existing PDF files in the uploads directory for testing
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    sample_pdf = os.path.join(uploads_dir, "input.pdf")
    
    if not os.path.exists(sample_pdf):
        print(f"Error: Sample PDF not found at {sample_pdf}")
        # Try to find any pdf in uploads
        pdfs = [f for f in os.listdir(uploads_dir) if f.endswith(".pdf")]
        if pdfs:
            sample_pdf = os.path.join(uploads_dir, pdfs[0])
            print(f"Using {sample_pdf} instead.")
        else:
            print("No PDF files found in uploads directory for testing.")
            return

    print(f"Reading {sample_pdf}...")
    with open(sample_pdf, "rb") as f:
        pdf_bytes = f.read()

    try:
        print("Uploading PDF...")
        asset_id = upload_pdf(pdf_bytes)
        print(f"Asset ID: {asset_id}")

        print("Converting to DOCX (this may take a few seconds)...")
        download_url = convert_to_docx(asset_id)
        print(f"Download URL: {download_url}")

        print("Downloading DOCX bytes...")
        docx_bytes = download_docx(download_url)
        print(f"Received {len(docx_bytes)} bytes.")

        output_path = os.path.join(os.path.dirname(__file__), "outputs", "test_output.docx")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(docx_bytes)
        print(f"Successfully saved test output to {output_path}")

    except Exception as e:
        print(f"An error occurred during verification: {e}")

if __name__ == "__main__":
    verify_conversion()
