import warnings
warnings.filterwarnings("ignore")

from paddleocr import PaddleOCR
from PIL import Image, ImageDraw, ImageFont

ocr = PaddleOCR(lang='hi')  # Hindi + English

results = ocr.predict('test.png')
page = results[0]

rec_texts = page['rec_texts']
rec_scores = page['rec_scores']
rec_polys = page['rec_polys']

image = Image.open('test.png').convert('RGB')
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("NotoSansDevanagari-Regular.ttf", 18)

for text, score, poly in zip(rec_texts, rec_scores, rec_polys):
    if score < 0.8:
        continue
    x1, y1 = poly[0]
    x3, y3 = poly[2]
    draw.rectangle([x1, y1, x3, y3], outline='red', width=2)
    draw.text((x1, y1-20), text, fill='red', font=font)

image.save('test_detected.png')
image.show()
