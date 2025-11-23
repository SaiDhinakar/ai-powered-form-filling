from unittest import TestCase
from src import detect_language

# Test cases for Indian languages

class TestLanguageDetection(TestCase):
    def test_detect_english(self) -> None:
        text = "Hello, how are you?"
        lang, confidence = detect_language(text)
        self.assertEqual(lang, "en")
        self.assertGreater(confidence, 0.8)

    def test_detect_hindi(self) -> None:
        text = "नमस्ते आप कैसे हैं"
        lang, confidence = detect_language(text)
        self.assertEqual(lang, "hi")
        self.assertGreater(confidence, 0.8)

    def test_detect_bengali(self) -> None:
        text = "আপনি কেমন আছেন?"
        lang, confidence = detect_language(text)
        self.assertEqual(lang, "bn")
        self.assertGreater(confidence, 0.8)

    def test_detect_tamil(self) -> None:
        text = "நீங்கள் எப்படி இருக்கிறீர்கள்?"
        lang, confidence = detect_language(text)
        self.assertEqual(lang, "ta")
        self.assertGreater(confidence, 0.8)

    def test_detect_telugu(self) -> None:
        text = "మీరు ఎలా ఉన్నారు?"
        lang, confidence = detect_language(text)
        self.assertEqual(lang, "te")
        self.assertGreater(confidence, 0.8)

    def test_detect_malayalam(self) -> None:
        text = "നിങ്ങൾ എങ്ങനെ ഉണ്ടാകുന്നു?"
        lang, confidence = detect_language(text)
        self.assertEqual(lang, "ml")
        self.assertGreater(confidence, 0.8)

    def test_detect_marathi(self) -> None:
        text = "तुम्ही कसे आहात?"
        lang, confidence = detect_language(text)
        self.assertEqual(lang, "mr")
        self.assertGreater(confidence, 0.8)

    def test_detect_gujarati(self) -> None:
        text = "તમે કેમ છો?"
        lang, confidence = detect_language(text)
        self.assertEqual(lang, "gu")
        self.assertGreater(confidence, 0.8)

    def test_detect_punjabi(self) -> None:
        text = "ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ?"
        lang, confidence = detect_language(text)
        self.assertEqual(lang, "pa")
        self.assertGreater(confidence, 0.8)    
