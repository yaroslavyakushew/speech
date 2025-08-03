from vosk import Model, KaldiRecognizer
import pyaudio
import json
import time

# Try both models to compare
# model = Model('/home/sergey/nano eng model')
model = Model('/home/sergey/spech nano model')  # Update this path
rec = KaldiRecognizer(model, 16000)

# Audio configuration optimizations
audio = pyaudio.PyAudio()
CHUNK = 4000  # You can try reducing this to 2000 for faster response
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
THRESHOLD = 0.1  # Adjust based on your microphone sensitivity

stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    input_device_index=None,  # Let PyAudio choose default
    stream_callback=None
)


def listening():
    last_partial = ""
    last_time = time.time()
    partial_interval = 0.5  # Seconds between partial updates

    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result()).get("text", "")
                if result:
                    yield f"[text] {result}"
                    rec.Reset()  # Reset for new recognition
            else:
                partial_result = json.loads(rec.PartialResult()).get("partial", "")
                current_time = time.time()

                if partial_result and partial_result != last_partial and (current_time - last_time) > partial_interval:
                    last_partial = partial_result
                    last_time = current_time
                    yield f"[partial] {partial_result}"

        except Exception as e:
            print(f"Error: {e}")
            continue


# Main loop with performance monitoring
start_time = time.time()
for i, text in enumerate(listening()):
    print(text)

    # Simple performance monitoring
    if i % 10 == 0:
        print(f"Processing rate: {i / (time.time() - start_time):.1f} iterations/sec")