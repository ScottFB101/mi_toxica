# spanish_teacher.py
# Audio-to-Text-to-Audio Spanish Practice Agent Skeleton
# Requires: openai, sounddevice or pyaudio, numpy, playsound or sounddevice

# --- Imports ---
import os
from dotenv import load_dotenv
import openai
import asyncio
import sounddevice as sd
import numpy as np
import tempfile
import soundfile as sf
import io
from pynput import keyboard  
import difflib

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY_spanish_teacher")
openai.api_key = api_key

# --- Audio Recording ---
async def record_audio(samplerate=16000, channels=1):
    import threading
    import time

    print("Press SPACE to start recording...")
    loop = asyncio.get_event_loop()
    recording = []
    stop_flag = threading.Event()
    start_flag = threading.Event()

    def on_press_start(key):
        if key == keyboard.Key.space:
            start_flag.set()
            return False

    def on_press_stop(key):
        if key == keyboard.Key.space:
            stop_flag.set()
            return False

    listener_start = keyboard.Listener(on_press=on_press_start)
    listener_start.start()
    while not start_flag.is_set():
        await asyncio.sleep(0.05)
    listener_start.stop()
    print("Recording... Press SPACE to stop.")

    def _record():
        with sd.InputStream(
            samplerate=samplerate, channels=channels, dtype="float32"
        ) as stream:
            while not stop_flag.is_set():
                data, _ = stream.read(1024)
                recording.append(data)

    record_thread = threading.Thread(target=_record)
    record_thread.start()
    listener_stop = keyboard.Listener(on_press=on_press_stop)
    listener_stop.start()
    while not stop_flag.is_set():
        await asyncio.sleep(0.05)
    record_thread.join()
    listener_stop.stop()
    print("Recording finished.")
    audio = np.concatenate(recording, axis=0)
    return np.squeeze(audio)


# --- Transcription (Speech-to-Text) ---
def transcribe_audio(audio_data, samplerate=16000):
    """Transcribe audio to text using OpenAI Whisper API."""
    # Save audio to a temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        sf.write(tmpfile.name, audio_data, samplerate)
        tmpfile.flush()
        tmpfile_name = tmpfile.name
    try:
        with open(tmpfile_name, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language="es",
            )
        return transcript.strip()
    finally:
        os.remove(tmpfile_name)


# --- LLM Response (Conversation/Correction) ---
def get_llm_response(text):
    """Send transcribed text to LLM and get a Spanish correction and response."""
    system_prompt = (
        "Eres un profesor de español conversacional. "
        "Corrige cualquier error en la frase del usuario. "
        "Primero, muestra la frase corregida (o la misma si está perfecta) en una línea que comience con 'Corrección:'. "
        "Luego, en una nueva línea, responde de manera natural para continuar la conversación en español. "
        "No expliques la corrección, solo muéstrala y luego responde."
    )
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.7,
        max_tokens=256,
    )
    return response.choices[0].message.content.strip()


# --- Translation (Spanish to English) ---
def translate_to_english(spanish_text):
    """Translate Spanish text to English using GPT."""
    system_prompt = (
        "You are a helpful assistant that translates Spanish to English. "
        "Only output the English translation, no extra commentary."
    )
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": spanish_text},
        ],
        temperature=0.3,
        max_tokens=256,
    )
    return response.choices[0].message.content.strip()


# --- Text-to-Speech (TTS) ---
def text_to_speech(text, voice="nova", model="tts-1", speed=1):
    """Convert text response to audio using OpenAI TTS API. Returns numpy array and sample rate. Slower speed for easier listening."""
    response = openai.audio.speech.create(
        model=model, voice=voice, input=text, response_format="wav", speed=speed
    )
    audio_bytes = response.content
    audio_buf = io.BytesIO(audio_bytes)
    audio_data, samplerate = sf.read(audio_buf, dtype="float32")
    # Normalize audio to -1.0 to 1.0 range if not already
    if audio_data.dtype != np.float32:
        audio_data = audio_data.astype(np.float32)
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        audio_data = audio_data / max_val
    return audio_data, samplerate


# --- Audio Playback ---
def play_audio(audio_data, samplerate):
    """Play audio back to the user using sounddevice. Ensures correct dtype and sample rate."""
    if audio_data.dtype != np.float32:
        audio_data = audio_data.astype(np.float32)
    sd.play(audio_data, samplerate)
    sd.wait()


def compute_similarity_score(original, corrected):
    """Compute a similarity score (0-100) between the user's original Spanish and the corrected version."""
    return int(
        difflib.SequenceMatcher(
            None, original.strip().lower(), corrected.strip().lower()
        ).ratio()
        * 100
    )


# --- Main CLI Loop ---
def main():
    import time

    print("Bienvenido a tu agente de práctica de español!")
    while True:
        print(
            "Habla ahora (presiona Espacio para comenzar y Espacio para terminar la grabación, o Ctrl+C para salir)..."
        )
        try:
            audio = asyncio.run(record_audio())
            text = transcribe_audio(audio)
            print(f"\nTú dijiste (español): {text}")
            user_translation = translate_to_english(text)
            print(f"Traducción al inglés: {user_translation}")
            response = get_llm_response(text)
            lines = response.split("\n", 1)
            correction = lines[0].replace("Corrección:", "").strip() if lines else ""
            reply = lines[1] if len(lines) > 1 else ""
            score = compute_similarity_score(text, correction)
            print(f"Puntaje de corrección: {score}/100")
            print(f"Corrección: {correction}")
            print(f"Agente responde: {reply}")
            translation = translate_to_english(reply)
            print(f"English: {translation}")
            response_audio, sr = text_to_speech(reply)
            play_audio(response_audio, sr)
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"Ocurrió un error: {e}")


if __name__ == "__main__":
    main()
