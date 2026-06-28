"""
Text-to-Speech service module.
Uses gTTS (Google Text-to-Speech) to generate MP3 audio bytes.
Serves as a server-side fallback when the browser's Web Speech API
is unavailable.
"""

import io

from config import LANGUAGE_MAP


class TTSService:
    """Generate speech audio from text using gTTS."""

    @staticmethod
    def generate_audio(
        text: str,
        lang_name: str = "English",
        slow: bool = False,
    ) -> bytes | None:
        """
        Generate MP3 audio bytes from *text*.

        Parameters
        ----------
        text : str
            The text to convert to speech.
        lang_name : str
            Display name of the language (e.g. "French").
        slow : bool
            If True, speak at a slower pace.

        Returns
        -------
        bytes | None
            MP3 audio bytes, or None on failure.
        """
        if not text or not text.strip():
            return None

        # Map codes to gTTS compatible codes (e.g., Hebrew 'he' -> 'iw', Javanese 'jv' -> 'jw')
        gtts_code_map = {
            "he": "iw",
            "jv": "jw",
        }
        lang_code = LANGUAGE_MAP.get(lang_name, "en")
        lang_code = gtts_code_map.get(lang_code.lower(), lang_code)

        try:
            from gtts import gTTS
            from gtts.lang import tts_langs

            # Check if code is supported in gTTS
            if lang_code not in tts_langs():
                # Try subtag as a fallback (e.g. 'zh-CN' -> 'zh' if needed)
                subtag = lang_code.split("-")[0]
                if subtag in tts_langs():
                    lang_code = subtag
                else:
                    return None

            tts = gTTS(text=text, lang=lang_code, slow=slow)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf.read()
        except Exception:
            return None
