import os
import pdfplumber
from langdetect import detect
from paddleocr import PaddleOCR
from pdf2image import convert_from_path


# Preload common OCR models (you can add more)
ocr_models = {
    "en": PaddleOCR(use_angle_cls=True, lang="en"),
    "ch": PaddleOCR(use_angle_cls=True, lang="ch"),
    "latin": PaddleOCR(use_angle_cls=True, lang="latin"),  # covers many EU languages
    "arabic": PaddleOCR(use_angle_cls=True, lang="arabic"),
    "korean": PaddleOCR(use_angle_cls=True, lang="korean"),
    "japan": PaddleOCR(use_angle_cls=True, lang="japan"),
    "hindi": PaddleOCR(use_angle_cls=True, lang="hindi"),
}

# Fallback multilingual (covers many languages)
fallback_ocr = PaddleOCR(use_angle_cls=True, lang="multilingual")


def detect_safe_language(text):
    try:
        return detect(text)
    except:
        return "unknown"


def choose_ocr_model(lang_code):
    # Map langdetect → PaddleOCR language codes
    mapping = {
        "en": "en",
        "zh-cn": "ch",
        "zh-tw": "ch",
        "ko": "korean",
        "ja": "japan",
        "ar": "arabic",
        "hi": "hindi",
        "ta": "latin",      # Tamil model not official; latin OCR works well
        "fr": "latin",
        "es": "latin",
        "de": "latin",
        "ru": "latin"
    }

    if lang_code in mapping and mapping[lang_code] in ocr_models:
        return ocr_models[mapping[lang_code]]

    return fallback_ocr  # fallback multilingual


def extract_text_multilang(pdf_path, dpi=300):
    final_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text()

            if text and text.strip():
                final_text += f"\n--- Page {page_number} ---\n{text}\n"
                continue

            # Page contains no digital text → use OCR
            images = convert_from_path(pdf_path, dpi=dpi,
                                       first_page=page_number, last_page=page_number)
            img = images[0]

            # First OCR with fallback multilingual model
            temp_result = fallback_ocr.ocr(img, cls=True)

            temp_text = " ".join([word[1][0] for line in temp_result for word in line])
            lang_code = detect_safe_language(temp_text)

            ocr_engine = choose_ocr_model(lang_code)

            # Use selected accurate model
            result = ocr_engine.ocr(img, cls=True)

            extracted = " ".join([w[1][0] for line in result for w in line])

            final_text += f"\n--- Page {page_number} (OCR: {lang_code}) ---\n{extracted}\n"

    return final_text

import os
# Usage
pdf_path = "your_file.pdf"
pdf_path = os.path.expanduser("~/Downloads/ATS_Resume_Sample.pdf")   # Replace with your file path
text = extract_text_multilang(pdf_path)
print(text)

