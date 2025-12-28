import asyncio
from googletrans import Translator

async def translate(text: str, src: str = "auto", dest: str = "en") -> str:
    """
    Translate the given text from src to dest using googletrans in a non-blocking way.
    """
    if not text:
        return ""

    translator = Translator()

    result = translator.translate(text, src=src, dest=dest)
    if asyncio.iscoroutine(result):
        result = await result
    print(text)
    # Some implementations return an object with a .text attribute, others return a string.
    return getattr(result, "text", result)

if __name__ == "__main__":
    async def main():
        text = "Bonjour tout le monde"
        translated_text = await translate(text, dest="en")
        print(f"Original: {text}")
        print(f"Translated: {translated_text}")

    asyncio.run(main())