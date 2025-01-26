import azure.cognitiveservices.speech as speechsdk
import base64
import hashlib
from pathlib import Path
import logging
from library.settings_manager import settings
import unicodedata


AUDIO_CACHE_DIR = Path("data") / "audio"
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def generate_filename(sentence):
    sentence_hash = hashlib.md5(sentence.encode('utf-8')).hexdigest()
    sanitized_chars = []
    for char in sentence_hash:
        category = unicodedata.category(char)
        if category.startswith('L') or category.startswith('N') or char.isalnum(): # Keep Letters, Numbers, and Alphanumeric (for safety)
            sanitized_chars.append(char)
        else:
            sanitized_chars.append('_') # Replace other chars with underscore

    filename = "".join(sanitized_chars)[:50]  # Limit length as before
    return filename


def generate_tts_audio_data(sentence):
    """Generates TTS audio data, using cache if available."""
    filename_base = generate_filename(sentence)
    audio_cache_file = AUDIO_CACHE_DIR / f"{filename_base}.wav"
    text_cache_file = AUDIO_CACHE_DIR / f"{filename_base}.txt"

    if audio_cache_file.exists() and text_cache_file.exists():
        try:
            with open(audio_cache_file, 'rb') as f_audio, open(text_cache_file, 'r', encoding='utf-8') as f_text:
                cached_sentence = f_text.read().strip()
                if cached_sentence == sentence.strip():
                    logging.info(f"Cache hit for sentence (prefix): {sentence[:30]}...")
                    audio_data_base64 = base64.b64encode(f_audio.read()).decode('utf-8')
                    return audio_data_base64
                else:
                    logging.warning(f"Hash collision or sentence mismatch for cached file (prefix): {sentence[:30]}"
                                    f"... Generating new TTS.")
        except Exception as e:
            logging.error(f"Error reading cache file {audio_cache_file}: {e}. Regenerating TTS.")

    speech_config = speechsdk.SpeechConfig(
        subscription=settings.get_setting('azure_tts.speech_key'),
        region=settings.get_setting('azure_tts.speech_region')
    )
    speech_config.speech_synthesis_voice_name = settings.get_setting('azure_tts.speech_voice')
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(audio_cache_file))
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    speech_synthesis_result = speech_synthesizer.speak_text(sentence)

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        try:
            with open(audio_cache_file, 'rb') as f_audio, open(text_cache_file, 'w', encoding='utf-8') as f_text:
                audio_data_base64 = base64.b64encode(f_audio.read()).decode('utf-8')
                f_text.write(sentence.strip())
            logging.info(f"TTS generated and cached for sentence (prefix): {sentence[:30]}...")
            return audio_data_base64
        except Exception as e:
            logging.error(f"Error saving or reading cached audio file {audio_cache_file}: {e}")
            return None
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        logging.error("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                logging.error("Error details: {}".format(cancellation_details.error_details))
        return None
    else:
        return None
