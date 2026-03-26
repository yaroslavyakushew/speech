from vosk import Model, KaldiRecognizer
import pyaudio, json, threading, serial, sys, difflib, time

# --- MODEL PATH ---
model_path = "C:/vosk-model-small-uk-v3-nano"

# --- GRAMMAR (короткий!) ---
grammar = '["вгору","вниз","вліво","вправо","стоп","старт","лікоть","кисть","плече","база","вихід"]'

model = Model(model_path)
rec = KaldiRecognizer(model, 16000, grammar)

# --- AUDIO ---
CHUNK = 2048
audio = pyaudio.PyAudio()

stream = audio.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=CHUNK)
stream.start_stream()

# --- SERIAL ---
usb_port = "COM7"
arduino = serial.Serial(usb_port, 9600, timeout=1)

# --- STATE ---
run = False
stopThread = threading.Event()

# ---------------- NORMALIZATION ----------------
def normalize(text):
    replacements = {
        "в гору": "вгору",
        "угору": "вгору",
        "в ліво": "вліво",
        "в право": "вправо",
        "локоть": "лікоть",
        "кисточка": "кисть"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.strip()

# ---------------- COMMANDS ----------------
def send(cmd):
    global run
    run = True
    arduino.write((cmd + "\n").encode())

def change(cmd):
    arduino.write((cmd + "\n").encode())

def up(): send("up")
def down(): send("down")
def left(): send("left")
def right(): send("right")

def elbow(): change("elbow")
def hand(): change("hand")
def shoulder(): change("shoulder")
def base(): change("base")

def start(): send("start")

def stop_cmd():
    global run
    arduino.write(b"stop\n")
    run = False

def exit_program():
    print("🔴 Вихід...")
    stopThread.set()
    stream.stop_stream()
    stream.close()
    audio.terminate()
    arduino.close()
    sys.exit(0)

# --- COMMAND DICTIONARY ---
commands = {
    "вгору": up,
    "вниз": down,

    "вліво": left,
    "ліво": left,

    "вправо": right,
    "право": right,

    "лікоть": elbow,
    "кисть": hand,
    "рука": hand,
    "плече": shoulder,

    "база": base,

    "старт": start,
    "стоп": stop_cmd,

    "вихід": exit_program,
    "вийти": exit_program
}

# --- FUZZY SEARCH ---
def find_command(text):
    keys = list(commands.keys())
    match = difflib.get_close_matches(text, keys, n=1, cutoff=0.65)
    return match[0] if match else None

# --- LISTENING ---
def listen():
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "").lower().strip()
            if text:
                yield text

# ---------------- MAIN LOOP ----------------
print("🎤 Слухаю...")

for raw_text in listen():
    print(f"[RAW] {raw_text}")

    text = normalize(raw_text)
    print(f"[NORMALIZED] {text}")

    command = None

    # 1. точний збіг
    if text in commands:
        command = text
    else:
        # 2. частковий збіг
        for key in commands:
            if key in text:
                command = key
                break

    # 3. fuzzy fallback
    if not command:
        command = find_command(text)

    # --- EXECUTION ---
    if command:
        print(f"✅ Команда: {command}")
        threading.Thread(target=commands[command]).start()
    else:
        print("❌ Не розпізнано")
