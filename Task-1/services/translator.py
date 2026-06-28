"""
Translation engine module.
Wraps deep-translator (GoogleTranslator) with auto-detect, error handling,
and performance tracking.  Pure Python — no framework dependencies.
"""

import time
from dataclasses import dataclass, asdict

from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

from config import LANGUAGE_MAP, CODE_TO_LANGUAGE


@dataclass
class TranslationResult:
    """Holds the result of a translation request."""

    translated_text: str
    source_language: str          # Display name
    target_language: str          # Display name
    detected_language: str | None  # Display name if auto-detected, else None
    elapsed_ms: float             # Response time in milliseconds
    success: bool
    error_message: str | None = None

    def to_dict(self) -> dict:
        """Serialize to a JSON-safe dictionary."""
        return asdict(self)


class TranslationEngine:
    """Core translation engine powered by Google Translate via deep-translator."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        auto_detect: bool = False,
    ) -> TranslationResult:
        """
        Translate *text* from *source_lang* to *target_lang*.

        Parameters
        ----------
        text : str
            The text to translate.
        source_lang : str
            Display name of the source language (e.g. "English").
        target_lang : str
            Display name of the target language (e.g. "Spanish").
        auto_detect : bool
            If True, detect the source language automatically.

        Returns
        -------
        TranslationResult
        """
        start = time.perf_counter()
        detected_name: str | None = None

        try:
            # Resolve target language code
            target_code = LANGUAGE_MAP.get(target_lang)
            if target_code is None:
                return self._error_result(
                    source_lang, target_lang, start,
                    f"Unsupported target language: {target_lang}",
                )

            # Resolve source language code
            if auto_detect:
                source_code = "auto"
                detected_code = self.detect_language(text)
                detected_name = CODE_TO_LANGUAGE.get(detected_code.lower(), detected_code)
            else:
                source_code = LANGUAGE_MAP.get(source_lang)
                if source_code is None:
                    return self._error_result(
                        source_lang, target_lang, start,
                        f"Unsupported source language: {source_lang}",
                    )

            translator = GoogleTranslator(source=source_code, target=target_code)
            result_text = translator.translate(text)

            elapsed = (time.perf_counter() - start) * 1000
            return TranslationResult(
                translated_text=result_text or "",
                source_language=detected_name if auto_detect else source_lang,
                target_language=target_lang,
                detected_language=detected_name,
                elapsed_ms=round(elapsed, 1),
                success=True,
            )

        except Exception as exc:
            return self._error_result(
                source_lang, target_lang, start,
                f"Translation failed: {exc}",
            )

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect the language of *text*.

        Returns the ISO-639 language code (e.g. ``"en"``).
        Falls back to ``"en"`` on failure.
        """
        try:
            return detect(text)
        except LangDetectException:
            return "en"

    @staticmethod
    def get_supported_languages() -> dict[str, str]:
        """Return the full mapping of display-name → code."""
        return dict(LANGUAGE_MAP)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _error_result(
        source: str, target: str, start: float, message: str,
    ) -> TranslationResult:
        elapsed = (time.perf_counter() - start) * 1000
        return TranslationResult(
            translated_text="",
            source_language=source,
            target_language=target,
            detected_language=None,
            elapsed_ms=round(elapsed, 1),
            success=False,
            error_message=message,
        )
