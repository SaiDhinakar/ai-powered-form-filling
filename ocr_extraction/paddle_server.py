import warnings
warnings.filterwarnings("ignore")

import time
import io
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from paddleocr import PaddleOCR
from PIL import Image, ImageDraw, ImageFont

# ✅ Initialize OCR models separately
ocr_hi = PaddleOCR(lang='hi')   # Hindi + English
ocr_ta = PaddleOCR(lang='ta')   # Tamil

app = FastAPI()

# -------------------------
# Hindi / English endpoint
# -------------------------
@app.post("/extract_ocr_hi/")
async def extract_ocr_hi(file: UploadFile = File(...)):
    return await run_ocr(file, ocr_hi, "NotoSansDevanagari-Regular.ttf", "Hindi OCR")

# -------------------------
# Tamil endpoint
# -------------------------
@app.post("/extract_ocr_ta/")
async def extract_ocr_ta(file: UploadFile = File(...)):
    return await run_ocr(file, ocr_ta, "NotoSansTamil-Regular.ttf", "Tamil OCR")


# -------------------------
# Shared OCR function
# -------------------------
async def run_ocr(file: UploadFile, ocr_model: PaddleOCR, font_file: str, label: str):
    start_time = time.time()

    # Read uploaded file into PIL Image
    image_bytes = await file.read()
    pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

    # Convert PIL -> numpy for PaddleOCR
    np_image = np.array(pil_image)

    # Run OCR
    results = ocr_model.predict(np_image)
    if not results:
        return {"error": f"No {label} results detected."}

    page = results[0]
    rec_texts = page['rec_texts']
    rec_scores = page['rec_scores']
    rec_polys = page['rec_polys']

    # Draw annotated boxes
    draw = ImageDraw.Draw(pil_image)
    try:
        font = ImageFont.truetype(font_file, 18)
    except:
        font = ImageFont.load_default()

    for text, score, poly in zip(rec_texts, rec_scores, rec_polys):
        if score < 0.8:
            continue
        x1, y1 = poly[0]
        x3, y3 = poly[2]
        draw.rectangle([x1, y1, x3, y3], outline='red', width=2)
        draw.text((x1, y1 - 20), text, fill='red', font=font)

    # Convert PIL -> bytes for Swagger UI
    img_bytes = io.BytesIO()
    pil_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    elapsed_ms = (time.time() - start_time) * 1000
    print(f"⚡ {label} + Annotation Time: {elapsed_ms:.2f} ms")

    return StreamingResponse(img_bytes, media_type="image/png")
