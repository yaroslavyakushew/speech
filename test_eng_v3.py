from vosk import Model, KaldiRecognizer 
import pyaudio, json, difflib, pigpio, time

grammar = '["up", "down", "front", "back", "to me", "from me"]' 
model = Model('/home/sergey/nano eng model')
rec = KaldiRecognizer(model, 16000, grammar)
audio = pyaudio.PyAudio()
pi = pigpio.pi()



CHUNK = 2048
SERVO_PIN = 14
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=CHUNK)
stream.start_stream()

def set_angle(angle):
    pulse_width = int(500 + (angle/180.0) * 2000)
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)

#Функции комманд
def up():
    a = 0
    for i in range(160):
        set_angle(a)
        a += 1
        time.sleep(0.01)
def down():
    a = 160
    for i in range(160):
        set_angle(a)
        a -= 1
        time.sleep(0.01)
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

try:
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

finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop