from vosk import Model, KaldiRecognizer
import pyaudio, json, time

model = Model('/home/sergey/nano eng model')
grammar = ["потужно", "перемога", "привіт"]

CHUNK = 16000

def listening():
    last_partial = ""
    last_time = time.time()
    it = 1
    
    while True:
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=2048)
        stream.start_stream()
        rec = KaldiRecognizer(model, 16000)
        
        
        while True:
            record = stream.read(CHUNK, exception_on_overflow=False)    
            ok = rec.AcceptWaveform(record)
            if ok and len(record) > 0:
                data = json.loads(rec.Result())
                text = data.get("text", "")
                if text:
                    last_partial = ""
                    stream.stop_stream()
                    stream.close()
                    audio.terminate()
                    yield f"[text] {text}"
                    break
            else:
                partial = json.loads(rec.PartialResult()).get("partial", "")
                now = time.time()
                if partial and last_partial != partial and now - last_time > it:
                    last_time = now
                    last_partial = partial
                    yield f"[partial] {partial}"
                    

for text in listening():
    print(text)