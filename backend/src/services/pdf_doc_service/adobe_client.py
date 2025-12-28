import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("ADOBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("ADOBE_CLIENT_SECRET")

TOKEN_URL = "https://ims-na1.adobelogin.com/ims/token/v3"
ASSET_URL = "https://pdf-services.adobe.io/assets"
EXPORT_URL = "https://pdf-services.adobe.io/operation/exportpdf"

_access_token = None
_token_expiry = 0


def _get_access_token():
    global _access_token, _token_expiry

    if _access_token and time.time() < _token_expiry:
        return _access_token

    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "openid,AdobeID,read_organizations,additional_info.projectedProductContext"
    }

    response = requests.post(TOKEN_URL, data=payload, timeout=30)
    response.raise_for_status()

    data = response.json()
    _access_token = data["access_token"]
    _token_expiry = time.time() + data["expires_in"] - 60

    return _access_token


def upload_pdf(pdf_bytes: bytes) -> str:
    print("Starting PDF upload to Adobe...")
    token = _get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "x-api-key": CLIENT_ID,
        "Content-Type": "application/json"
    }

    # Step 1: Create an asset and get upload URI
    payload = {
        "mediaType": "application/pdf"
    }
    print("Requesting upload URI...")
    response = requests.post(ASSET_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    upload_data = response.json()
    upload_uri = upload_data["uploadUri"]
    asset_id = upload_data["assetID"]
    print(f"Asset ID created: {asset_id}")

    # Step 2: Upload the actual file content
    upload_headers = {
        "Content-Type": "application/pdf"
    }
    print("Uploading binary data...")
    put_response = requests.put(upload_uri, headers=upload_headers, data=pdf_bytes, timeout=30)
    put_response.raise_for_status()
    print("Upload successful.")

    return asset_id


def convert_to_docx(asset_id: str) -> str:
    print(f"Starting conversion for asset: {asset_id}")
    token = _get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "x-api-key": CLIENT_ID,
        "Content-Type": "application/json"
    }

    payload = {
        "assetID": asset_id,
        "targetFormat": "docx"
    }

    # Step 1: Start the export operation
    print("Initiating export operation...")
    response = requests.post(EXPORT_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    # Operation is asynchronous, get status URL from Location header
    status_url = response.headers.get("Location")
    if not status_url:
        raise Exception("Failed to get job status URL from Adobe API")
    print(f"Job status URL obtained: {status_url}")

    # Step 2: Poll for completion
    max_retries = 30  # 60 seconds max
    retries = 0
    while retries < max_retries:
        print(f"Polling status (attempt {retries + 1})...")
        status_response = requests.get(status_url, headers=headers, timeout=30)
        status_response.raise_for_status()
        job_data = status_response.json()
        
        status = job_data.get("status")
        print(f"Current status: {status}")

        if status == "completed" or status == "done":
            print("Conversion completed successfully.")
            return job_data["asset"]["downloadUri"]
        elif status == "failed":
            print("Conversion failed.")
            raise Exception(f"Adobe conversion failed: {job_data}")
        
        retries += 1
        time.sleep(2)  # Wait before polling again
    
    raise Exception("Adobe conversion timed out after matching max retries.")


def download_docx(download_url: str) -> bytes:
    print("Downloading converted DOCX...")
    # Some download URIs might be short-lived signed URLs that don't need auth headers
    response = requests.get(download_url, timeout=30)
    response.raise_for_status()
    print("Download successful.")
    return response.content
