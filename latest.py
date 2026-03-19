from itertools import zip_longest
import config
from vosk import Model, KaldiRecognizer
import pyaudio, json, difflib, time, threading, serial, sys, os
from pathlib import Path
import serial.tools.list_ports
# --- Voice grammar ---

globalGrammar = config.globalGrammar
commands = config.commands
handParts = config.handParts
specialCommands = config.specialCommands
multiCommands = config.multiCommands


#Нужно добавить определение платформы и порта, где ардуино, желательно б это с скриптом установки совместить
path = Path.home() / "speech" / "nano eng model"
strpath = str(path)
print(strpath)


model = Model(strpath)
rec = KaldiRecognizer(model, 16000, globalGrammar)



# Далее закоментированн код, ибо для дебага использовался ввод из клавиатуры. Если есть микрофон и роборука - можно раскоментировать
audio = pyaudio.PyAudio()


def find_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description:
            return port.device

        # 2. Проверка по VID:PID (для оригинальных плат и некоторых клонов)
        # VID 0x2341 — официальный ID Arduino
        if port.vid == 0x2341:
            return port.device

        # 3. Для дешевых клонов на чипе CH340 (часто определяются так)
        if "CH340" in port.description or "USB-SERIAL" in port.description:
            return port.device

    return None
usb_port = find_arduino()
#Инциализация порта для отправления команд на роборуку в системе
# arduino = serial.Serial(usb_port, 9600, timeout=1)

# --- Servo setup ---
CHUNK = 2048
SERVO_PIN = 14
angle = 0
max_angle = 150
stop = False
run = False

#Для инициализации прослушивания ввода с микрофона

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
    for phrase in multiCommands:
        text = text.replace(phrase, phrase.replace(" ", "_"))
    words = text.split()

    words = [word.replace("_", " ") for word in words]

    # debug(words)
    for word in words:
        for i, j, w in zip_longest(commands, handParts, specialCommands):
            if word == i:
                found_commands.append((word, "command"))
            if word == j:
                found_commands.append((word, "hand"))
            if word == w:
                found_commands.append((word, "special command"))

    for command, flag in found_commands:
        print(f"✅ Command recognized: {command}")
        if flag == "command":
            threading.Thread(target=writing, args=(command,)).start()
        elif flag == "hand":
            threading.Thread(target=changePin, args=(command,)).start()
        elif flag == "special command":
            if command == "exit": exit1()
            if command == "stop": stop_cmd()
    
    if len(found_commands) == 0:
        print("❌ Unrecognized or partial command.")

arduino.close()
