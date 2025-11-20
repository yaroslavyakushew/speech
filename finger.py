from vosk import Model, KaldiRecognizer 
import pyaudio, json, difflib, time, threading, serial, sys, os

# --- Voice grammar ---
grammar = '["up", "down", "exit", "stop"]'
all_way = "~/speech/model"

model = Model(os.path.expanduser(all_way))
rec = KaldiRecognizer(model, 16000, grammar)
usb_port = "COM7"

audio = pyaudio.PyAudio()
arduino = serial.Serial(usb_port, 9600, timeout=1)

# --- Servo setup ---
CHUNK = 2048
SERVO_PIN = 14
angle = 0
max_angle = 150
stop = False
run = False

stream = audio.open(format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=CHUNK
)
stream.start_stream()

def writing(text):
    global run
    run = True
    arduino.write(text.encode())

def changePin(text):
    arduino.write(text.encode())


def readArduino():
    try:
        global run, keywords
        while not stopThread.is_set():
            line = arduino.readline().decode('utf-8').strip()
            if (line == "run false"):
                run = False
                keywords = full_dict
        time.sleep(0.1)
    except Exception as e:
        print("where arduino?")

stopThread = threading.Event()
arduinoThread = threading.Thread(target=readArduino, daemon=False)
arduinoThread.start()


def up(): writing("up\n")
def down():writing("down\n")

def stop_cmd():
    global run
    arduino.write(b"stop\n")
    run = False

def exit1():
    stopThread.set()
    arduinoThread.join()
    stream.stop_stream()
    stream.close()
    audio.terminate()
    arduino.close()
    sys.exit(0)

# --- Keywords dictionary ---
full_dict = {
    "up": up,
    "down": down,
    "exit": exit1
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


for text in listening():
    print(f"[text] {text}")
    text = text.lower().strip()

    found_commands = []
        
    if run == True:
        keywords = stop_dict
    else:
        keywords = full_dict


    if len(found_commands) <= 1:
        for key in sorted(keywords, key=lambda k: (-len(k.split()), -len(k))):
            key_l = key.lower()
            if key_l in text:
                found_commands.append(key)
                text = text.replace(key_l, " ")

    # 4. Execute command if found
    for command in found_commands:
        if command in keywords:
            print(f"✅ Command recognized: {command}")
            if command != "exit":
                threading.Thread(target=keywords[command], args=()).start()
            else:
                keywords[command]()
    
    if len(found_commands) == 0:
        print("❌ Unrecognized or partial command.")

arduino.close()