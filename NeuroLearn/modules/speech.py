"""
Speech Module - Text-to-Speech and basic Speech-to-Text helpers
Uses edge-tts (high quality, free) and SpeechRecognition
"""

import os
import tempfile
import asyncio
from typing import Optional
import streamlit as st


class SpeechHandler:
    """Handles TTS and provides STT helper."""

    def __init__(self):
        self.voice = "en-US-AriaNeural"  # Natural female voice
        # Alternatives: en-US-GuyNeural, en-IN-NeerjaNeural, en-IN-PrabhatNeural

    async def _generate_tts(self, text: str, output_path: str):
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"TTS Error: {e}")
            return False

    def text_to_speech(self, text: str) -> Optional[str]:
        """
        Convert text to speech and return path to audio file.
        Truncates very long text for practicality.
        """
        if not text or len(text.strip()) < 5:
            return None

        # Limit length for demo
        if len(text) > 1200:
            text = text[:1200] + "... (truncated for audio)"

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                output_path = fp.name

            success = asyncio.run(self._generate_tts(text, output_path))
            if success and os.path.exists(output_path):
                return output_path
        except Exception as e:
            print(f"TTS generation failed: {e}")
        return None

    def set_voice(self, voice_name: str):
        self.voice = voice_name


def get_available_voices():
    return {
        "US Female (Aria)": "en-US-AriaNeural",
        "US Male (Guy)": "en-US-GuyNeural",
        "Indian Female (Neerja)": "en-IN-NeerjaNeural",
        "Indian Male (Prabhat)": "en-IN-PrabhatNeural",
        "UK Female (Sonia)": "en-GB-SoniaNeural"
    }
