import azure.cognitiveservices.speech as speechsdk
import base64
from settings_manager import settings
import logging


def generate_tts_audio_data(sentence):
    speech_config = speechsdk.SpeechConfig(
        subscription=settings.get_setting('azure_tts.speech_key'),
        region=settings.get_setting('azure_tts.speech_region')
    )
    speech_config.speech_synthesis_voice_name = settings.get_setting('azure_tts.speech_voice')

    audio_config = speechsdk.audio.AudioOutputConfig(filename=None)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    speech_synthesis_result = speech_synthesizer.synthesize_speech(sentence)

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        audio_data = speech_synthesis_result.audio_data
        # Base64 encode the audio data for sending over HTTP (JSON-friendly)
        base64_audio = base64.b64encode(audio_data).decode('utf-8')
        return base64_audio
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        logging.error("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                logging.error("Error details: {}".format(cancellation_details.error_details))
        return None
    else:
        return None
