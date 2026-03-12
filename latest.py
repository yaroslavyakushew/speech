from itertools import zip_longest

from vosk import Model, KaldiRecognizer
import pyaudio, json, difflib, time, threading, serial, sys

# --- Voice grammar ---
globalGrammar = '["up", "down", "left", "right", "to me", "from me", "stop", "base", "exit", "arm up", "arm down", "elbow", "hand", "brush", "inner elbow", "shoulder"]'
commands = ["up", "down", "left", "right", "exit", "from me", "to me", "stop", "arm up", "arm down"]
handParts = ["base", "hand", "elbow", "brush", "inner elbow", "shoulder"]
#Хуево подтягиваются слова из словарей

#raspberry_way = '/home/sergey/nano eng model'
windows_way = 'C:/Users/Student/speech/nano eng model'

model = Model(windows_way)
rec = KaldiRecognizer(model, 16000, globalGrammar)
usb_port = "COM7"

audio = pyaudio.PyAudio()
#arduino = serial.Serial(usb_port, 9600, timeout=1)

# --- Servo setup ---
CHUNK = 2048
SERVO_PIN = 14
angle = 0
max_angle = 150
stop = False
run = False

# stream = audio.open(format=pyaudio.paInt16,
#    channels=1,
#    rate=16000,
#    input=True,
#    frames_per_buffer=CHUNK
#)
#stream.start_stream()

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

def debug(list):
    for i,j in list:
        print(j)
stopThread = threading.Event()
arduinoThread = threading.Thread(target=readArduino, daemon=False)
arduinoThread.start()



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


#--- Listening generator ---
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

for text in printing():
    print(f"[text] {text}")
    text = text.lower().strip()
    print(text)

    found_commands = []
    def checking():
        words = text.split()
       # debug(words)
        for i, j, word in zip_longest(commands, handParts, words): # возможно проблема в зипе относительно проблемы ниже
            print(f"I: {i}")
            print(f"J: {j}")
            if word == i: # Некорректная проверка, почему то слишком много аппендов
                found_commands.append((word, "command"))
            if word == j:
                found_commands.append((word, "hand")) # Если передавать первым словом, остальные команды не распознаются

    checking()

    # 4. Execute command if found
    debug(found_commands)
    for command, flag in found_commands:
        if command in globalGrammar:
            print(f"✅ Command recognized: {command}")
            if command != "exit" and command != "stop": #Мульти комманды некорректно обрабатываются
                if flag == "command": # У нас может быть фраза, имеющая 2 типа комманд: и команды и изменения пинов.
                    # В таком случае на 1 слово 2 команды выполняться будет. Фиксить надо добавлением к каждому слову флага
                    threading.Thread(target=writing, args=(command)).start()
                elif flag == "hand":
                    threading.Thread(target=changePin, args=(command)).start()
            else:
                if command == "exit": exit1()
                if command == "stop": stop_cmd()
    
    if len(found_commands) == 0:
        print("❌ Unrecognized or partial command.")

arduino.close()
