import threading
import pygame
import io
import soundfile as sf
from kokoro_onnx import Kokoro
import os
import urllib.request
import time
import numpy as np
import queue  #  Queue for streaming
import re  #  Sentence detection

#  MONKEY PATCH (Standard Fix)
if not hasattr(np, "original_load"):
    np.original_load = np.load


def smart_load(*args, **kwargs):
    if 'allow_pickle' not in kwargs:
        kwargs['allow_pickle'] = True
    return np.original_load(*args, **kwargs)


np.load = smart_load

class TTS_Engine:
    _is_speaking = False
    _stop_event = threading.Event()
    _current_thread = None
    _kokoro = None

    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self._ensure_models_exist()

        if TTS_Engine._kokoro is None:
            print("Loading Kokoro ONNX on CPU...")
            try:
                # Standard Opset 20 Model
                TTS_Engine._kokoro = Kokoro("kokoro-v0_19.onnx", "voices.bin")
                print("Kokoro Loaded Successfully (Opset 20 Supported). 🟢")
            except Exception as e:
                print(f"CRITICAL ERROR: {e}")

        self.hindi_voice = "af_bella"
        self.english_voice = "af_sarah"

    def _ensure_models_exist(self):
        files = ["kokoro-v0_19.onnx", "voices.bin"]
        base_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/"

        for file in files:
            if not os.path.exists(file):
                print(f"Downloading {file}...")
                try:
                    urllib.request.urlretrieve(base_url + file, file)
                    print(f"Downloaded {file}")
                except Exception as e:
                    print(f"Failed to download {file}: {e}")

    @classmethod
    def stop(cls):
        cls._is_speaking = False
        cls._stop_event.set()
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

    # NEW STREAMING FUNCTION
    def speak_stream(self, text_generator):
        """
        Streaming Mode: LLM se chunks lekar turant bolna shuru karta hai.
        Latnecy: ~1s
        """
        if TTS_Engine._kokoro is None:
            print("❌ Kokoro not loaded.")
            return

        TTS_Engine.stop()
        TTS_Engine._stop_event.clear()
        TTS_Engine._is_speaking = True

        # Audio Queue (Generator -> Queue -> Player)
        audio_queue = queue.Queue()

        # Thread 1: Text Process & Generate Audio
        gen_thread = threading.Thread(
            target=self._stream_generator,
            args=(text_generator, audio_queue)
        )

        # Thread 2: Play Audio from Queue
        play_thread = threading.Thread(
            target=self._stream_player,
            args=(audio_queue,)
        )

        gen_thread.start()
        play_thread.start()

    def _stream_generator(self, text_generator, audio_queue):
        sentence_buffer = ""
        # Regex: Newline, Comma, Fullstop etc.
        sentence_endings = re.compile(r'(?<=[.?!])\s|\n|[,]')

        try:
            for chunk in text_generator:
                if TTS_Engine._stop_event.is_set(): break

                sentence_buffer += chunk

                parts = sentence_endings.split(sentence_buffer)

                if len(parts) > 1:
                    to_process = parts[:-1]
                    sentence_buffer = parts[-1]

                    for sentence in to_process:
                        if len(sentence.strip()) > 1:
                            audio_data = self._generate_audio_bytes(sentence)
                            if audio_data:
                                # ✅ CHANGE: Audio ke saath Text bhi bhejo (Tuple)
                                audio_queue.put((audio_data, sentence.strip()))

            if sentence_buffer.strip():
                audio_data = self._generate_audio_bytes(sentence_buffer)
                if audio_data:
                    # ✅ CHANGE: Last chunk
                    audio_queue.put((audio_data, sentence_buffer.strip()))

        except Exception as e:
            print(f"Streaming Gen Error: {e}")
        finally:
            audio_queue.put(None)


    def _generate_audio_bytes(self, text):
        """Helper: Text -> WAV Bytes"""
        try:
            # Generate Audio (Fastest Settings)
            samples, sample_rate = TTS_Engine._kokoro.create(
                text,
                voice=self.english_voice,
                speed=1.0,
                lang="en-us"
            )

            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, samples, sample_rate, format='WAV')
            audio_buffer.seek(0)
            return audio_buffer
        except Exception as e:
            print(f"Gen Error: {e}")
            return None

    def _stream_player(self, audio_queue):
        """Queue se audio nikal kar play karta hai aur text print karta hai"""
        first_chunk = True
        start_time = time.perf_counter()

        while True:
            if TTS_Engine._stop_event.is_set(): break

            # Queue se packet nikalo
            packet = audio_queue.get()

            if packet is None:  # End of stream
                break

            # Packet unpack karo (Audio + Text)
            audio_data, text_segment = packet

            # Latency calculate karo (sirf pehle chunk ke liye meaningful hai, par har baar dikha sakte ho)
            current_latency = (time.perf_counter() - start_time) * 1000

            if first_chunk:
                print(f"🚀 Streaming Started! (First Byte: {current_latency:.0f}ms)")
                first_chunk = False

            # Play Audio
            try:
                # 🗣️ PRINT TEXT SYNCED WITH AUDIO
                print(f"🤖 Sarah: '{text_segment}'")

                pygame.mixer.music.load(audio_data)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    if TTS_Engine._stop_event.is_set():
                        pygame.mixer.music.stop()
                        return
                    time.sleep(0.05)
            except Exception as e:
                print(f"Playback Error: {e}")

        TTS_Engine._is_speaking = False

    # --- OLD SIMPLE SPEAK (Backward Compatibility) ---
    def speak(self, text):
        # Ise use karo agar text chhota hai (Not streaming)
        # Main logic wahi hai bas generator bana ke stream ko pass kar do
        def simple_gen():
            yield text

        self.speak_stream(simple_gen())