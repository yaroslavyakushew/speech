from vosk import Model, KaldiRecognizer 
import pyaudio, json, difflib, pigpio, time, threading
import serial
import struct

# --- Serial communication setup ---
# !coment! - Add serial communication with Arduino
try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Adjust port as needed
    time.sleep(2)  # Wait for Arduino to initialize
    print("Connected to Arduino")
except:
    print("Arduino not connected, running in simulation mode")
    arduino = None

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
    def __init__(self, SERVO_PIN1, angle1, max_angle1, min_angle, delay):
        self.angle1 = angle1
        self.max_angle1 = max_angle1
        self.SERVO_PIN1 = SERVO_PIN1
        self.delay = delay
        self.min_angle = min_angle
    
    def set_angle(self, a):
        if arduino:
            # Send command to Arduino
            command = f"SET{self.SERVO_PIN1:02d}{a:03d}"
            arduino.write(command.encode())
        else:
            # Local simulation
            pulse_width = 500 + (a/self.max_angle1) * 2000
            pi.set_servo_pulsewidth(self.SERVO_PIN1, pulse_width)
    
    def movement(self, reverse):
        global stop, run
        run = True
        time_a = 0
        stop = False
        
        if not reverse:
            time_a = self.max_angle1 - self.angle1
        else:
            time_a = self.angle1 - self.min_angle
            
        for i in range(time_a):
            if stop: 
                break
            if not reverse:
                self.angle1 += 1
            else:
                self.angle1 -= 1
            self.set_angle(self.angle1)
            time.sleep(self.delay)
        run = False
        
    def up(self):
        if arduino:
            # Send command to Arduino
            command = f"UP{self.SERVO_PIN1:02d}"
            arduino.write(command.encode())
        else:
            self.movement(True)

    def down(self):
        if arduino:
            # Send command to Arduino
            command = f"DN{self.SERVO_PIN1:02d}"
            arduino.write(command.encode())
        else:
            self.movement(False)

# --- Create servo list ---
classList = []
    
# --- Command functions ---
def hand(list1):
    global SERVO_PIN
    SERVO_PIN = 14  # Default hand servo pin
    print(f"Hand servo selected: PIN {SERVO_PIN}")
    
def up(list1):
    for obj in list1:
        if obj.SERVO_PIN1 == SERVO_PIN:
            obj.up()
            break
    
def down(list1):
    for obj in list1:
        if obj.SERVO_PIN1 == SERVO_PIN:
            obj.down()
            break

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
    if arduino:
        arduino.write(b"STOP")  # Send stop command to Arduino

# --- Keywords dictionary ---
full_dict = {
    "up": up,
    "down": down,
    "hand": hand,
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
try:
    # Create servo objects for all servos
    servos_config = [
        (16, 0, 150, 0, 0.08),  # kleshnya
        (5, 0, 150, 0, 0.08),   # kist_rotary
        (4, 0, 150, 0, 0.08),   # kist_bend
        (0, 0, 150, 0, 0.08),   # shoulder
        (14, 0, 150, 0, 0.08),  # collarbone (hand)
        (12, 0, 150, 0, 0.08)   # guohu
    ]
    
    for config in servos_config:
        classList.append(Test(*config))
    
    # Initialize servos to minimum angle
    for servo in classList:
        servo.set_angle(servo.min_angle)
    
    # Use hand servo by default
    hand(classList)
    
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
        else:
            print("❌ Unrecognized or partial command.")
        
finally:
    # Cleanup
    if arduino:
        arduino.close()
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()
