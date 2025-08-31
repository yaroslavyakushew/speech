from vosk import Model, KaldiRecognizer 
import pyaudio, json, difflib, pigpio, time, threading

# --- Voice grammar ---
grammar = '["up", "down", "front", "back", "to me", "from me", "stop", "hand"]'  
model = Model('/home/sergey/nano eng model')
rec = KaldiRecognizer(model, 16000, grammar)

audio = pyaudio.PyAudio()
pi = pigpio.pi()

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


class Test:
    def __init__(self, SERVO_PIN1, angle, max_angle):
        self.angle = angle
        self.max_angle = max_angle
        self.SERVO_PIN1 = SERVO_PIN1
    def up():
        movement(SERVO_PIN1, self.angle, True)

    def down():
        movement(SERVO_PIN1, self.angle, False)

    
classList = []
    
# --- Servo functions ---
    
def set_angle(a, SERVO_PIN):
        pulse_width = 500 + (a/180.0) * 2000
        pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)
        
def movement(SERVO_PIN, angle1, reverse):
    global stop, run
    run = True
    time_a = 0
    stop = False
    if reverse == False:
        time_a = max_angle - angle
    else:
        time_a = angle
    for i in range(time_a):
        if stop: break
        set_angle(angle, SERVO_PIN)
        if reverse == False:
            angle += 1
        else:
            angle -= 1
        time.sleep(0.08)
    run = False

# --- Command functions ---
def hand(list1):
    global SERVO_PIN
    for obj in list1.list:
        if obj.SERVO_PIN1 == 14:
            SERVO_PIN = obj.SERVO_PIN1
            angle = obj.angle
def up(list1):
    for Cls in list1:
        obj = Cls()
        if obj.SERVO_PIN1 == SERVO_PIN:
            obj.up()
    
def down(list1):
    for obj in list1:
        if obj.SERVO_PIN1 == SERVO_PIN:
            obj.down()
    movement(SERVO_PIN, angle, False)
def front(list1):
    print("front to 60 degrees")

def back(list1):
    print("back")

def to_me(list1):
    print("to me")

def from_me(list1):
    print("from me")

def stop_cmd(list1):
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
    "from me": from_me,
    "hand": hand
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
try:
    set_angle(angle, SERVO_PIN)
    test1 = Test(14, 0, 150)
    classList.insert(0, test1)
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
            threading.Thread(target=keywords[found_command], args=(classList)).start()
            print(angle)
        else:
            print("❌ Unrecognized or partial command.")
        
        

finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()
