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

def movement(SERVO_PIN, angle1, reverse):
    global stop, run
    run = True
    time_a = 0
    stop = False
    if reverse == False:
        time_a = max_angle - angle1
    else:
        time_a = angle1
    for i in range(time_a):
        if stop: break
        set_angle(angle1, SERVO_PIN)
        if reverse == False:
            angle1 += 1
        else:
            angle1 -= 1
        time.sleep(0.08)
    run = False


class Test:
    def __init__(self, SERVO_PIN1, angle1, max_angle1):
        self.angle1 = angle
        self.max_angle1 = max_angle1
        self.SERVO_PIN1 = SERVO_PIN1
    
    
    def movement(self, SERVO_PIN1, angle1, reverse):
        global stop, run
        run = True
        time_a = 0
        stop = False
        if reverse == False:
            time_a = self.max_angle1 - self.angle1
        else:
            time_a = self.angle1
        for i in range(time_a):
            if stop: break
            set_angle(self.angle1, self.SERVO_PIN1)
            if reverse == False:
                self.angle1 += 1
            else:
                self.angle1 -= 1
            time.sleep(0.08)
        run = False
        
    def up(self):
        self.movement(self.SERVO_PIN1, self.angle1, True)

    def down(self):
        self.movement(self.SERVO_PIN1, self.angle1, False)

    
classList = []
    
# --- Servo functions ---
    
def set_angle(a, SERVO_PIN):
        pulse_width = 500 + (a/180.0) * 2000
        pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)
        

# --- Command functions ---
def hand(list1):
    global SERVO_PIN
    for obj in list1.list:
        if obj.SERVO_PIN1 == 14:
            SERVO_PIN = obj.SERVO_PIN1
            angle = obj.angle
def up(list1):
    for obj in list1:
        if obj.SERVO_PIN1 == SERVO_PIN:
            obj.up()
    
def down(list1):
    for obj in list1:
        if obj.SERVO_PIN1 == SERVO_PIN:
            obj.down()
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
            threading.Thread(target=keywords[found_command], args=(classList, )).start()
            print(test1.angle1)
        else:
            print("❌ Unrecognized or partial command.")
        
        

finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()
