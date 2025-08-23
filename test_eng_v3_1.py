from vosk import Model, KaldiRecognizer 
import pyaudio, json, difflib, pigpio, time

grammar = '["up", "down", "front", "back", "to me", "from me"]' 
model = Model('/home/sergey/nano eng model')
rec = KaldiRecognizer(model, 16000, grammar)
audio = pyaudio.PyAudio()
pi = pigpio.pi()



CHUNK = 2048
SERVO_PIN = 14
angle = 0
max_angle = 150
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=CHUNK)
stream.start_stream()

def set_angle(a):
    pulse_width = int(500 + (a/180.0) * 2000)
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)
    
def movement(SERVO_PIN):
    global angle
    for i in range(angle):
        set_angle(angle)
        angle -= 1
        print(angle)
        time.sleep(0.01)
   
def r_movement(SERVO_PIN):
    global angle, max_angle
    time_a = max_angle - angle
    for i in range(time_a):
        set_angle(angle)
        angle += 1
        print(angle)
        time.sleep(0.01)
  

#Функции комманд
def up():
    movement(SERVO_PIN)
def down():
    r_movement(SERVO_PIN)
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
    set_angle(angle)
    for text in listening():
        print(f"[text] {text}")
        if text in keywords:
            print(f"✅ Command recognized: {text}")
            keywords[text]()
        
            
        else:
            match = difflib.get_close_matches(text, n=1, cutoff=0.6) #Ця частина має проблеми
            if match:
                print(f"✅ Command recognized: {text}")
                keywords[match[0]]()
            else:
                print("❌ Unrecognized or partial command.")

finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop