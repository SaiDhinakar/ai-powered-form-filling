from googletrans import Translator

def translate(text: str, src: str = "auto", dest: str = "en") -> str:
    if not text:
        return ""

    translator = Translator()
    result = translator.translate(text, src=src, dest=dest)
    return getattr(result, "text", result)


if __name__ == "__main__":
    async def main():
        text = "Bonjour tout le monde"
        translated_text = await translate(text, dest="en")
        print(f"Original: {text}")
        print(f"Translated: {translated_text}")
