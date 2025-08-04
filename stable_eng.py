from vosk import Model, KaldiRecognizer
import pyaudio, json, time

model = Model('/home/sergey/nano eng model')
rec = KaldiRecognizer(model, 16000)
audio = pyaudio.PyAudio()
CHUNK=4000
stream = audio.open(format = pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=CHUNK)
stream.start_stream()



def listening():
    while True:
        record = stream.read(CHUNK, exception_on_overflow=False)
        if rec.AcceptWaveform(record) and len(record):
            data = json.loads(rec.Result())
            result = data.get("text", "")
            if result:
                yield f"[text] {result}"
               
            
         
        
for text in listening():
    print(text)
