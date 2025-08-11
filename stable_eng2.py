from vosk import Model, KaldiRecognizer 
import pyaudio, json, difflib

grammar = '["up", "down", "front", "back", "to me", "from me"]' 
model = Model('/home/sergey/nano eng model')
rec = KaldiRecognizer(model, 16000, grammar)
audio = pyaudio.PyAudio()


CHUNK = 2048
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=CHUNK)
stream.start_stream()

#Функции комманд
def up():
    print("up to 60 degrees")
def down():
    print("down to 60 degrees")
def front():
    print("front to 60 degrees")
def back():
    print("back")
def to_me():
    print("to me")
def from_me():
    print("from me")
def stop():
    print("stop")


def listening():
    while True:
        record = stream.read(CHUNK, exception_on_overflow=False)
        if rec.AcceptWaveform(record):
            data = json.loads(rec.Result())
            result = data.get("text", "")
            if result:
                yield result

keywords = {"up": up, "down": down, "front": front, "back": back, "to me": to_me, "from me": from_me, "stop": stop} #Сюда добавлять команды

for text in listening():
    print(f"[text] {text}")
    if text in keywords:
        print(f"✅ Command recognized: {text}")
        keywords[text]()
        
            
    else:
        match = difflib.get_close_matches(text, n=1, cutoff=0.6)
        if match:
            print(f"✅ Command recognized: {text}")
            keywords[match[0]]()
        else:
            print("❌ Unrecognized or partial command.")
