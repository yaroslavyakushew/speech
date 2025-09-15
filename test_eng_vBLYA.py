from vosk import Model, KaldiRecognizer 
import pyaudio, json, difflib, time, threading, serial

# --- Voice grammar ---
grammar = '["up", "down", "front", "back", "to me", "from me", "stop", "hand"]'
raspberry_way = '/home/sergey/nano eng model'
linux_way = "/home/thrashir/speech small model"
model = Model(linux_way)
rec = KaldiRecognizer(model, 16000, grammar)
usb_port = "/dev/ttyUSB1"

audio = pyaudio.PyAudio()
arduino = serial.Serial(usb_port, 9600, timeout=1)

# --- Servo setup ---
CHUNK = 2048
SERVO_PIN = 14
angle = 0
max_angle = 150
stop = False
run = False

stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=CHUNK
)
stream.start_stream()



def up():
    arduino.write(b"Potuzhno!!!!\n")

def down():
    arduino.write(b"Down!\n")
def front():
    print("front to 60 degrees")

def back():
    print("back")

def to_me():
    print("to me")

def from_me():
    print("from me")

def stop_cmd():
    global stop
    print("stop")
    stop = True

# --- Keywords dictionary ---
full_dict = {
    "up": up,
    "down": down,
    "front": front,
    "back": back,
    "to me": to_me,
    "from me": from_me
}
stop_dict = {"stop": stop_cmd}
keywords = full_dict

# --- Listening generator ---
def listening():
    while True:
        record = stream.read(CHUNK, exception_on_overflow=False)
        if rec.AcceptWaveform(record):
            data = json.loads(rec.Result())
            result = data.get("text", "").strip()
            if result:
                yield result

def printing(): #For test program, when i can`t talking
    while True:
        text = input("Type text: ")
        if text:
            yield text
# --- Main program ---

for text in listening():
    print(f"[text] {text}")
    text = text.lower().strip()

    found_command = None
        
    if run == True:
        keywords = stop_dict
    else:
        keywords = full_dict

    # 1. Check multi-word commands first
    for cmd in ["to me", "from me"]:
        if cmd in text:
            found_command = cmd
            break

    # 2. Check single-word commands
    if not found_command:
        words = text.split()
        for word in words:
            if word in keywords:
                found_command = word
                break

    # 3. Fuzzy matching (per word)
    if not found_command:
        words = text.split()
        for word in words:
            match = difflib.get_close_matches(word, keywords.keys(), n=1, cutoff=0.7)
            if match:
                found_command = match[0]
                break

    # 4. Execute command if found
        
    if found_command:
        print(f"✅ Command recognized: {found_command}")
        threading.Thread(target=keywords[found_command], args=()).start()     
    else:
        print("❌ Unrecognized or partial command.")
        
