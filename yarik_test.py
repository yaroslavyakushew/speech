from vosk import Model, KaldiRecognizer
import pyaudio, json, time

model = Model('/home/sergey/spech nano model')
grammar = ["потужно","перемога","привіт"]

CHUNK=4000




def listening():
    last_partial = ""
    last_time = time.time()
    it = 1
    
    while True:
        audio = pyaudio.PyAudio()
        stream = audio.open(format = pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=CHUNK)
        stream.start_stream()
        rec = KaldiRecognizer(model, 16000)
        while True:
            record = stream.read(CHUNK, exception_on_overflow=False)
        if rec.AcceptWaveform(record) and len(record) > 0:
            data = json.loads(rec.Result())
            result = data.get("text", "")
            if result:
                last_partial = ""
                rec.Reset()
                stream.stop_stream()
                stream_close()
                audio.terminate()
                
                yield f"[text] {data}"
                break
        else:
            data = json.loads(rec.PartialResult()).get("partial", "")
            now = time.time()
            if data and data != last_partial and now - last_time > it:
                last_partial = data
                last_time = now
                yield f"[partial] {data}"
            
   
        
for text in listening():
    print(text)
