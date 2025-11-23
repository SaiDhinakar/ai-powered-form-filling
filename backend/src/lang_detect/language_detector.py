import fasttext
import os

path = os.path.join("src","lang_detect","lid.176.ftz") if __name__ != '__main__' else "lid.176.ftz'"
print(path)
model = fasttext.load_model(path)

def detect(text: str) -> tuple[str, float]:
    lang, confidence = model.predict(text)
    return lang[0].replace("__label__", ""), confidence[0]

if __name__ == "__main__":
    text = "வணக்கம் நீங்கள் எப்படி இருக்கிறீர்கள்"
    lang, confidence = detect(text)

    print("Detected:", lang)
    print("Confidence:", confidence)

