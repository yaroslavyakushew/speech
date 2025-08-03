from vosk import Model, KaldiRecognizer
import pyaudio, json
import numpy as np

# Nano model and grammar
model = Model('/home/sergey/spech nano model')
rec = KaldiRecognizer(model, 16000)

# PyAudio settings
CHUNK = 800
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=CHUNK)
stream.start_stream()

def amplify_audio(data, gain=2.5):
    audio_data = np.frombuffer(data, dtype=np.int16)
    louder_data = np.clip(audio_data * gain, -32768, 32767).astype(np.int16)
    return louder_data.tobytes()

def listen():
    last_result = ""
    while True:
        audio_data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = amplify_audio(audio_data, gain=2.5)

        if rec.AcceptWaveform(audio_data):
            result = json.loads(rec.Result())
            text = result.get("text", "").strip()

            # Only output new, non-empty results
            if text and text != last_result:
                last_result = text
                print(f"[text] {text}")
                # You can add action triggers here:
                if "вперед" in text:
                    print("рухаюсь вперед")
                elif "вниз" in text:
                    print("опускаюсь вниз")
                elif "вправо" in text:
                    print("повертаюсь вправо")
                elif "вліво" in text:
                    print("повертаюсь вліво")

# Start listening
listen()
