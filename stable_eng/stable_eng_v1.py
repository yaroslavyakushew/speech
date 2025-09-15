from vosk import Model, KaldiRecognizer 
import pyaudio, json

grammar = '["up", "down", "front", "back", "to me", "from me"]' 
model = Model('/home/sergey/nano eng model')
rec = KaldiRecognizer(model, 16000, grammar)
audio = pyaudio.PyAudio()

CHUNK = 2048
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=CHUNK)
stream.start_stream()

def listening():
    while True:
        record = stream.read(CHUNK, exception_on_overflow=False)
        if rec.AcceptWaveform(record):
            data = json.loads(rec.Result())
            result = data.get("text", "")
            if result:
                yield result

keywords = {"up", "down", "front", "back", "to me", "from me"}

for text in listening():
    print(f"[text] {text}")
    if text in keywords:
        print(f"✅ Command recognized: {text}")
    else:
        print("❌ Unrecognized or partial command.")
