from faster_whisper.transcribe import Segment
import speech_recognition as sr
from faster_whisper import WhisperModel
import numpy as np
import time

Model_Size = "medium"
Device = "cuda"
Compute_type = "float16"

start_time = time.time()

model = WhisperModel(Model_Size, device=Device, compute_type=Compute_type)
print(f"Model loaded in {time.time() - start_time} seconds")

def listen_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            print("Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            raw_data = audio.get_raw_data(convert_rate=16000, convert_width=2)
            audio_np = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            segments, info = model.transcribe(audio_np, beam_size=5)
            text = " ".join([segment.text for segment in segments])

            if text.strip():
                print(text)
                return text
            else:
                return None
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

def check_exit(text):
    if not text:
        return False
    exit_phrases = ["exit", "quit", "stop", "terminate", "later", "talk soon", "bye", "adios"]
    if any(phrase in text.lower() for phrase in exit_phrases):
        return True
    return False

if __name__ == "__main__":
    try:
        while True:
            text = listen_and_transcribe()
            if check_exit(text):
                print("Exiting...")
                break
    except KeyboardInterrupt:
        print("Program interrupted by user.")